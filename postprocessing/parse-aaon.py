from numpy import *
from matplotlib.pyplot import *
from physics import *
import numpy.lib as nplib
import scikits.statsmodels.api as sm
from process import contiguous_regions
from parametrics import month_splits

def wgraph(a):
    figure()
    wret = humidity_ratio(a.RH_AHretrn_frc_AVG, a.T_AHreturn_C_AVG*1.8+32)
    wsupp = humidity_ratio(a.RH_AHsupp1_frc_AVG, a.T_AHsupply1_C_AVG*1.8+32)
    scatter(wret, wsupp)
    plot((0,0.04), (0,0.04), 'r')
    xlim(0, 0.035)
    ylim(0, 0.035)
    xlabel('Humidity Ratio, Return')
    ylabel('Humidity Ratio, Supply')
    savefig('aaon-w-scatter-all.png')

def Wsup(a):
    return humidity_ratio(a.RHsup, a.Tsup*1.8+32)

def Wret(a):
    return humidity_ratio(a.RHret, a.Tret*1.8+32)

def coil_w_scat(a, subset=None, color='k'):
    if subset==None:
        subset = ones(a.RHret.shape).fill(True)
    scatter(humidity_ratio(a.RHret[subset], a.Tret[subset]*1.8+32), humidity_ratio(a.RHsup[subset], a.Tsup[subset]*1.8+32), color=color)

def coil_w_hmap2(a, subset=None):
    if subset==None:
        subset = ones(a.RHret.shape).fill(True)
    hexbin(humidity_ratio(a.RHret[subset], a.Tret[subset]*1.8+32), humidity_ratio(a.RHsup[subset], a.Tsup[subset]*1.8+32))

def coil_w_hmap(a):
    hexbin(humidity_ratio(a.RHret, a.Tret*1.8+32), humidity_ratio(a.RHsup, a.Tsup*1.8+32))

def coil_t_scat(a, subset=None, color='k'):
    if subset==None:
        subset = (ones(a.RHret.shape) == 1) # how to make this easier to read?
    scatter(a.Tret[subset], a.Tsup[subset], color=color)

def coil_dt_arr(a, subset=None):
    if subset==None:
        subset = (ones(a.RHret.shape) == 1) # how to make this easier to read?
    return (a.Tsup[subset] - a.Tret[subset])

def ret_t_range(a, low, high):
    return ( (a.Tret > low) & (a.Tret < high))

# from http://www.rigtorp.se/2011/01/01/rolling-statistics-numpy.html
def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return nplib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def force_reshape(arr, n):
    "reshape arr to have n columns, truncating trailing elements as necesary"
    drop = arr.reshape(-1).shape[0] % n
    return arr[:-drop].reshape(-1, n)

def reshape_all(a, n):
    ret = Empty()
    for k, v in a.__dict__.iteritems():
        ret.__dict__[k] = force_reshape(v,n)
    return ret

# TODO add some useful methods to this
class Empty:
    pass

def subsets(wraps):
    # use `all` along axis 1 to select n-min intervals with a single operating state
    return [('c1', all(wraps['Sc1']==1, axis=1) & all(wraps['Sc2']==0, axis=1) ),
            # ('c2dn', all(wraps['Sc2']==1, axis=1)  & all(wraps['Sdh'] == 0, axis=1) ),
            # ('c2dy', all(wraps['Sc2']==1, axis=1) & all(wraps['Sdh'] == 1, axis=1) ),
            ('c2', all(wraps['Sc2']==1, axis=1)),
            ('dh', all(wraps['Sc1']==0, axis=1) & all(wraps['Sdh'] == 1, axis=1) & all(wraps["Sht"] == 0, axis=1) ),
            ('ht', all(wraps["Sht"] == 1, axis=1) ),
            ('off', all(wraps['Sdh']==0, axis=1) & all(wraps['Sc1']==0, axis=1) & all(wraps['Sht']==0, axis=1) )]

    

def c2_by_ahu_kw(a):
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict([(k, force_reshape(a.__dict__[k], 5)) for k in keys])
    for name, subset in [('c2hi', all(wraps['kWah'] > 0.6, axis=1) & all(wraps['Sc2']==1, axis=1) & all(isnan(wraps['kWhp']) == False, axis=1) ),
                         ('c2lo', all(wraps['kWah'] < 0.4, axis=1) & all(wraps['Sc2']==1, axis=1) & all(isnan(wraps['kWhp']) == False, axis=1 ) )]:
        print("{0} has length {1}".format(name, subset.sum()))
        r = Empty()
        r.__dict__.update( dict([(k, mean(wraps[k], axis=1)[subset]) for k in keys]) )
        ret.__dict__[name] = r
    return ret

def c2_by_ontime(a):
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict([(k, force_reshape(a.__dict__[k], 5)) for k in keys])
    mode = ( all(wraps['Sc2']==1, axis=1) & all(invert(isnan(wraps['kWhp'])), axis=1) )
    for i in xrange(6):
        name = "{0}m".format(i*5)
        print(name)
        subset = mode[i+1:] & invert(mode[:-i-1]) # i*5 minutes ago, was not in c2
        for j in xrange(i):
            subset = subset & mode[j+1:j-i] # was in c2 between (i-1)*5 min, and now
        print("{0} has length {1}".format(name, subset.sum()))
        r = Empty()

        ret.__dict__[name] = r
    return ret
    
    
def five_fold(a):
    "return 5-minute average values, breaking up intervals by operating state"
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict([(k, force_reshape(a.__dict__[k], 5)) for k in keys])
    # group into 5-minute intervals
    for name, subset in subsets(wraps):
        print("{0} has length {1}".format(name, subset.sum()))
        r = Empty()
        r.__dict__.update( dict([(k, mean(wraps[k], axis=1)[subset]) for k in keys]) )
        ret.__dict__[name] = r
    return ret

def steady_state_15(a):
    """return 5-minute average values, breaking up intervals by operating state,
    where state has been constant for 15 minutes"""
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict([(k, force_reshape(a.__dict__[k], 5)) for k in keys])
    for name, subset in subsets(wraps):
        steady = subset[2:] & subset[1:-1] & subset[:-2]
        print("{0} has length {1}".format(name, steady.sum()))
        r = Empty()
        # first 2 intervals are not part of steady because we don't know the history
#        r.__dict__.update( dict([(k, mean(wraps[k], axis=1)[2:][steady]) for k in keys]) )
        for k in keys:
            if k == 'cond':
                r.__dict__[k] = sum(wraps[k], axis=1)[2:][steady]
            else:
                r.__dict__[k] = mean(wraps[k], axis=1)[2:][steady]
        ret.__dict__[name] = r
    return ret        


def steady_state_30(a):
    """return 5-minute average values, breaking up intervals by operating state,
    where state has been constant for 30 minutes"""
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict([(k, force_reshape(a.__dict__[k], 5)) for k in keys])
    for name, subset in subsets(wraps):
        steady = subset[5:] & subset[:-5] & subset[1:-4] & subset[2:-3] & subset[3:-2] & subset[4:-1]
        print("{0} has length {1}".format(name, steady.sum()))
        r = Empty()
        # first 2 intervals are not part of steady because we don't know the history
        for k in keys:
            if k == 'cond':
                r.__dict__[k] = sum(wraps[k], axis=1)[5:][steady]
            else:
                r.__dict__[k] = mean(wraps[k], axis=1)[5:][steady]
        ret.__dict__[name] = r
    return ret        

def hour_state(a):
    ret = Empty()
    keys = a.__dict__.keys()
    wraps = dict( [(k, force_reshape(a.__dict__[k], 60)) for k in keys])
    for name, subset in subsets(wraps):
        print("{0} has length {1}".format(name, subset.sum()))
        r = Empty()
        # first 2 intervals are not part of steady because we don't know the history
        for k in keys:
            if k == 'cond':
                r.__dict__[k] = sum(wraps[k], axis=1)[subset]
            else:
                r.__dict__[k] = mean(wraps[k], axis=1)[subset]
        ret.__dict__[name] = r
    return ret

# 2d heatmap w/ squares, doesn't quite work, use hexbin instead
# def heatmap(x, y, bins=50, **kwargs):
#     heatmap, xedges, yedges = histogram2d(x, y, bins=50)
#     extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

#     imshow(heatmap, extent=extent, **kwargs)
#     show()

def coil_dw(arr):
    return humidity_ratio(arr.RHsup, arr.Tsup*1.8+32) - humidity_ratio(arr.RHret, arr.Tret*1.8+32)

def state_hist(states, var, bins=50, labels=None, xl=None):
    for i, s in enumerate(states):
        subplot(len(states), 1, i)
        if type(var) is str:
            hist(s.__dict__[var], bins)
        elif type(var) is type(coil_dw):
            hist(var(s), bins)
        else:
            raise(Exception('var must be str or function'))
    if xl:
        xlabel(xl)
    if labels:
        for i, s in enumerate(labels):
            subplot(len(states), 1, i)
            title(s)

def cent_diff(ar):
    # special case endpoints
    d0 = (ar[1] - ar[-1])/2
    dn = (ar[0] - ar[-2])/2
    d  = (ar[2:] - ar[:-2])/2
    return hstack((d0, d, dn))

def dh_subset_by_Trefr(a):
    '''cooling coil is cold & reheat coil is hot defines DH mode
    No dehumidification happens when Tevap is above about -4
    +10 threshold from 2012-04-04-kWah-dT.png; could justify going to +6 or +20,
    but it's hard to imagine DH with reheat that low,
    and I think the Tevap constraint will filter in between.'''
    Tevap = a.Tr2
    Tret = a.Tret
    Treheat = a.Te1
    Tamb = a.Tamb
    return (Tevap - Tret < -4) & (Treheat - Tret > 10) & (a.kWah < 0.15) & (a.t > 2010197000000)  & (isnan(a.kWhp) == False) & (isnan(a.kWah) == False) & (Tamb > 20)
    # try accepting more data, to see beginning of DH call
    #return (Tevap < Tret) & (Treheat > Tret) & (a.kWah < 0.15) & (a.t > 2010197000000)
    # isnan conditions make a mess of the ontime calcs, because they don't reflect the actual state of the AAON, but rather sensor / datalogger problems

def dh_by_Trefr(a):
    return afilter(a, dh_subset_by_Trefr(a))

def state_plot(a, dt):
    Lht = plot( force_reshape(a.Sht, dt).mean(axis=1) + 3.6, 'r')
    Lc2 = plot( force_reshape(a.Sc2, dt).mean(axis=1) + 2.4, 'b')
    Ldd = plot( force_reshape(a.Sdd, dt).mean(axis=1) + 1.2, 'c')
    Ldh = plot( force_reshape(a.Sdh, dt).mean(axis=1), 'g')
    Sdh = where((a.Tr2 - a.Tret < -4) & (a.Te1 - a.Tret > 1), 1, 0)
    Lrefr = plot( force_reshape(Sdh, dt).mean(axis=1) - 1.2, 'm')
    ylim(-1.4, 4.8)
    title('Fractional Runtime')
#    legend([Lht, Lc2, Ldd, Ldh, Lrefr], ['Heating', 'Cooling Stg 2', 'DH Disable', 'DH Call', 'Evap Cold, Reheat Hot'])

def afilter(a, cond):
    ret = Empty()
    for key, value in a.__dict__.iteritems():
        ret.__dict__[key] = value[cond]
    return ret

def nfilter(a, n, start=0):
    if start+n > a.t.size:
        n = a.t.size - start -1
    return afilter(a, (a.t<a.t[n+start]) & (a.t>= a.t[start]))

def exes(a):
    """returns an array with a bunch of inputs for OLS regression"""
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack( (
        a.Tamb, a.Tret, Wret, a.Tamb**2, a.Tamb*Wret, Wret**2, a.Tret**2)))

def wyes(c):
    """returns a function of exes using the provided coefficients"""
    return (lambda a: dot(a,c))

def by_wret(Tamb, Tret, Wret):
    o = ones(Wret.shape)
    return sm.add_constant(column_stack( (
        Tamb*o, Tret*o, Wret, Tamb**2*o, (Tamb*o)*Wret, Wret**2, Tret**2*o )))

def tret_wret(a):
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack((
        a.Tret, Wret, a.Tret*2)))

def tamb_wret(a):
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack((
        a.Tamb, Wret, a.Tamb*Wret)))

def ret2(a):
    return sm.add_constant(column_stack((
        a.Tret, Wret(a), a.Tret**2, a.Tret*Wret(a), Wret(a)**2)))

def by_wret2(Tret, Wret):
    o = ones(Wret.shape)
    return sm.add_constant(column_stack((
        Tret*o, Wret, Tret**2*o, (Tret*o)*Wret, Wret**2)))

def tamb2(a):
    return sm.add_constant(column_stack((
        a.Tamb**2, a.Tamb)))

def wret2(a):
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack((
        Wret**2, Wret)))

def ts_to_minute(time):
    '''convert a timestep of the form yyyyjjjhhmmss to a minute from 0 AD'''
    # s = time % 10**2
    m = (time // 10**2) % 10**2
    h = (time // 10**4) % 10**2
    j = (time // 10**6) % 10**3
    y = (time // 10**9) % 10**4
    #return (y,j,h,m,s) # test
    return m + 60*h + 60*24*j + 60*8760*y

def long_events(condition, length):
    bounds = contiguous_regions(condition)
    long_enough =  (bounds[:,1] - bounds[:,0] >= length)
    return bounds[long_enough]

def subplot_f(n, f, *argc):
    for i in xrange(1,n+1):
        subplot(n,1,i)
        f(*argc)

def ts_to_julian(time):
    return (time // 10**6) % 10**3


# def ontime(st):
#     ret = zeros(st.t.shape)
#     for i in xrange(ret.shape[0]):
#         if i == 0:
#             continue
#         if ts_to_minute(st.t[i]) - ts_to_minute(st.t[i-1]) == 1:
#             ret[i] = ret[i-1]+1
#         else:
#             ret[i] = 0
#     return ret

# This code takes about an hour to run, with dh and ontime(dh) as st and ont:
# def bad_ontime0(a, st, ont):
#     ret = zeros(a.shape)
#     for o, t in zip(ont, dh.t):
#         dh_ont[a.t == t] = o
#     return ret

# the uncommented ontime below takes 0.3 seconds
# It took me all day to come up with this version, but really, 4 orders of magnitude?
# it still has the for loop, it ditches the zip, but it looks like a.t == t is actually the problem

# In [435]: %timeit a.t == a.t[500000]
# 10 loops, best of 3: 53.1 ms per loop
# (* .053 (expt 10 6) (/ 1 3600.0)) 14.722222222222221
# so O(n^2) is bad

# def ontime1(cond):
#     ret = np.zeros(cond.shape)
#     for i in xrange(ret.size):
#         if i == 0:
#             continue
#         if cond[i]:
#             ret[i] = ret[i-1]+1
#         else:
#             ret[i] = 0
#     return ret

def ontime(cond):
    ret = np.zeros(cond.shape)
    ontime = 0
    for i in xrange(ret.size):
        if cond[i]:
            ontime += 1
            ret[i] = ontime
        else:
            ontime = 0
    return ret

# this looks O(n), like ontime2
# extra inputs, to keep extraneous calculations out of what is measured
# def bad_ontime3(at, ct, ont):
#     i = 0
#     j = 0
#     ret = zeros(at.shape)
#     while (i < at.size) & (j < ont.size):
#         if at[i] == ct[j]:
#             ret[i] = ont[j]
#         elif at[i] < ct[j]:
#             i += 1
#         else:
#             j += 1

def ts_to_iso(date):
    j = ts_to_julian(date)
    y = int((date // 10**9) % 10**4)
    # count how many last-days-of-month are less than j
    ms = array([0]+month_splits)
    m = (j > ms).sum()
    d = int(j - ms[m-1]) # days after last day of previous month
    return '{y}-{m:02}-{d:02}'.format(**locals())

def iso_to_ts(date):
    y = int(date[:4])
    m = int(date[5:7])
    d = int(date[8:10])
    ms = array([0]+month_splits)
    j = ms[m-1] + d
    return y*10**9 + j*10**6
