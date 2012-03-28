from numpy import *
from matplotlib.pyplot import *
from physics import *
import numpy.lib as nplib
import scikits.statsmodels.api as sm

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

def state_hist(states, var, bins=50):
    for i, s in enumerate(states):
        subplot(len(states), 1, i)
        hist(s.__dict__[var], bins)

def dh_subset_by_Trefr(a, dt):
    '''cooling coil is cold & reheat coil is hot defines DH mode
    1 C is a first pass to avoid noise near the many zero points; tune empirically
    No dehumidification happens when Tevap is above about -4'''
    Tevap = force_reshape(a.Tr2, dt).mean(axis=1)
    Tret = force_reshape(a.Tret, dt).mean(axis=1)
    Treheat = force_reshape(a.Te1, dt).mean(axis=1)
    return (Tevap - Tret < -4) & (Treheat - Tret > 1)

def dh_by_Trefr(a):
    ret = Empty()
    dh = dh_subset_by_Trefr(a, 5)
    for key, value in a.__dict__.iteritems():
        if key == 'cond':
            ret.__dict__[key] = sum(force_reshape(value, 5), axis=1)[dh]
        else:
            ret.__dict__[key] = mean(force_reshape(value, 5), axis=1)[dh]
    return ret

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

def exes(a):
    """returns an array with a bunch of inputs for OLS regression"""
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack( (
        a.Tamb, a.Tret, Wret, a.Tamb**2, a.Tamb*Wret, Wret**2, a.Tret**2)))

def wyes(c):
    """returns a function of exes using the provided coefficients"""
    return (lambda a: dot(a,c))

def tret_wret(a):
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack((
        a.Tret, Wret, a.Tret*2)))

def tamb_wret(a):
    Wret = humidity_ratio(a.RHret, a.Tret*1.8+32)
    return sm.add_constant(column_stack((
        a.Tamb, Wret, a.Tamb*Wret)))
