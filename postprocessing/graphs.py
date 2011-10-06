# coding= utf-8
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from parametrics import by_month, month_names, daily_total, daily_mean
from physics import humidity_ratio

summary_path = '../summary'

def plot_TRH(hourly, name='', interactive=False):
    fig = plt.figure()
    line_ti, = plt.plot(hourly.Ti)
    line_ti.set_linewidth(0.2)
    ax1, = fig.axes
    ax1.axis([0,8760,20,95])
    line_to, = plt.plot(hourly.To)
    line_to.set_linewidth(0.2)
    plt.ylabel('degrees F')
    plt.xlabel('Hour of Year')
    ax2 = ax1.twinx()
    line_rhi, = ax2.plot(hourly.RHi, label='Indoor RH', linewidth=0.2, color='r')
    plt.legend([line_to, line_ti, line_rhi], ['Outdoor T', 'Indoor T', 'Indoor RH'], loc='lower right')
    plt.axes(ax2)
    plt.ylabel('percent RH')
    ax2.axis([0,8760,0,100])
    plt.title('{0}: Annual Conditions'.format(name))
    #plt.show()
    fig.savefig( '{1}/{0}-annual-trh.png'.format(name, summary_path) )
    plt.close()

def plot_Wrt(hourly, name='', interactive=False):
    fig = plt.figure()
    line_Wi, = plt.plot(hourly.Wi, linewidth=0.2)
    line_Wo, = plt.plot(hourly.Wo, linewidth=0.2)
    plt.ylabel('water content of air (by mass)')
    plt.xlabel('Hour of Year')
    ax1, = fig.axes
    ax2 = ax1.twinx()
    plt.axes(ax2)
    line_RTFc, = plt.plot(hourly.RTFc, linewidth=0.2, color='r')
    ax2.axis([0,8760,-0.5,2.5])
    plt.ylabel('Fraction of Hour')
    plt.legend([line_Wo, line_Wi, line_RTFc], ['Outdoor W', 'Indoor W', 'Cooling Runtime'], loc='upper left')
    plt.title('{0}: Moisture Removal'.format(name))
    fig.savefig('{1}/{0}-annual-moisture.png'.format(name, summary_path))
    plt.close()

def plot_rh_hist(hourly, name='', interactive=False):
    fig = plt.figure()
    plt.hist(hourly.RHi,50)
    plt.xlabel('percent RH')
    plt.ylabel('Number of Hours')
    plt.title('{0}: Indoor RH Histogram'.format(name))
    fig.savefig( '{1}/{0}-rh-histogram.png'.format(name, summary_path) )
    plt.close()
    
def plot_rh_hist_daily(hourly, name='', interactive=False):
    fig = plt.figure()
    plt.hist(hourly.RHi,50)
    plt.xlabel('average RH [%]')
    plt.ylabel('Number of Days')
    plt.title('{0}: Indoor RH Histogram'.format(name))
    fig.savefig( '{1}/{0}-rh-histogram-daily.png'.format(name, summary_path) )
    plt.close()

def plot_t_hist(hourly, name='', interactive=False):
    fig = plt.figure()
    plt.hist(hourly.Ti,50)
    plt.xlabel('degrees F')
    plt.ylabel('Number of Hours')
    plt.title('{0}: Indoor T Histogram'.format(name))
    fig.savefig( '{1}/{0}-ti-histogram.png'.format(name, summary_path) )
    plt.close()

def plot_AC_hist(hourly, name='', interactive=False):
    fig = plt.figure()
    xs = np.linspace(60,110,51)
    cooling = np.where(hourly.RTFc >= 0.05, 1, 0)
    ys = []
    for low, high in zip(xs, xs[1:]):
        in_bin = np.where( (hourly.To>=low) & (hourly.To<high) )
        ys.append( cooling[in_bin].sum() )
    ys.append( np.where( hourly.To >= xs[-1], cooling, 0).sum() )
    plt.bar(xs, ys, width=1)
    plt.xlabel('Outdoor T (degrees F)') # TODO why doesn't unicode ° render in png graph?
    plt.ylabel('Hours with at least 3 minutes Cooling')
    plt.title( '{0}: Cooling Hours Breakdown'.format(name) )
    fig.savefig( '{1}/{0}-AC_hist'.format(name, summary_path) )
    plt.close()

def plot_window_gain(hourly, name='', interactive=False):
    def helper(name, gain):
        fig = plt.figure()
        lines = []
        plt.hold(True)
        for month in by_month(gain):
            l, = plt.plot(month.mean(axis=0))
            lines.append(l)
        plt.xlabel('Hour of Day')
        plt.ylabel('Net Gain')
        plt.legend(lines, month_names, loc='upper left')
        plt.title('{0} By Month'.format(name))
        fig.savefig('{1}/{0}-by-month.png'.format(name, summary_path))
        plt.close()
    try:
        for key in ['SOLS', 'SOLE', 'SOLN', 'SOLW']:
            helper('{0}-{1}'.format(name, key), hourly[key])
    except KeyError:
        print "Not enough data for plot_window_gain; skipping: {0}".format(name)

def rh_hist_compare(hs, names):
    ret = plt.hist(np.vstack([h.RHi for h in hs]).transpose(), np.linspace(0,100,51), label=names)
    plt.xlim(40,90)
    plt.xlabel('RH [%]')
    plt.ylabel('Number of Hours')
    plt.legend()
    return ret

def ac_bal_point(h, name='', interactive=False):
    fig = plt.figure()
    rt = daily_total(h.RTFc) # AC runtime
    ts = daily_mean(h.To)
    ch = np.where(rt>0) # cooling hours
    trlim = (60,90)
    p = np.polyfit(ts[ch], rt[ch], 1)
    tr = np.poly1d(p)
    plt.scatter(ts, rt, marker='+', s=10, linewidths=0.1, color='r')
    # don't plot balance point, Hugh says
    #plt.plot(trlim, tr(trlim), 'r')
    plt.ylim(0,40)
    plt.xlabel('Outdoor Daily Avg T [degF]')
    plt.ylabel('Daily AC Runtime [hours]')
    plt.title('{0}:Cooling Balance'.format(name))
    if name:
        fig.savefig('{1}/{0}-AC-balance.png'.format(name, summary_path))
        if not interactive: # if name is provided, assume called from script, unless interactive set
            plt.close()
    return p[1]/p[0] # Balance Point below which no AC is needed

def plot_humidity_ratio(hourly, name='', interactive=False):
    fig = plt.figure()
    plt.scatter(daily_mean(hourly.Wo), daily_mean(hourly.Wi))
    plt.xlabel('Outdoor Humidity Ratio')
    plt.ylabel('Indoor Humidity Ratio')
    plt.title('{0}: Daily Humidity Ratio'.format(name))
    if name:
        fig.savefig('{1}/{0}-wi-wo.png'.format(name, summary_path))
        if not interactive:
            plt.close()
                 
def plot_daily_psychrometric(hourly, name='', interactive=False):
    fig = plt.figure()
    ti = daily_mean(hourly.Ti)
    wi = daily_mean(hourly.Wi)
    rt = daily_total(hourly.RTFc) # cooling runtime
    cd = np.where(rt > 0)[0] # cooling days
    ncd = np.where(rt <= 0)[0] # non-cooling days
    plt.scatter(ti[cd], wi[cd], color='b')
    plt.scatter(ti[ncd], wi[ncd], color='r')
    # plot some lines of constant RH
    ts = np.linspace(65,85,5)
    for rh in np.linspace(0.1, 1, 10):
        plt.plot(ts, humidity_ratio(rh, ts), 'k')
    plt.xlabel('Indoor Temperature [degF]')
    plt.ylabel('Indoor Humidity Ratio')
    plt.title('{0}: Psychrometric Chart'.format(name))
    # RH labels on right hand side
    ax1 = plt.axes()
    ax2 = ax1.twinx()
    ax2.get_yaxis().set_major_locator(ticker.FixedLocator(humidity_ratio(np.linspace(0,1,11), 85)/0.030)) # TODO don't hardcode limits
    ax2.get_yaxis().set_major_formatter(ticker.FixedFormatter(np.linspace(0,100,11)))
    plt.ylabel('Indoor RH [%]')
#    ax2.get_yaxis().set_major_locator(ticker.FixedLocator(np.linspace(0,1,11)))
    if name:
        fig.savefig('{1}/{0}-psychrometric.png'.format(name, summary_path))
        if not interactive:
            plt.close()
    
def psych_chart(T, W):
    fig = plt.figure()
    plt.scatter(T, W)
    ts = np.linspace(0,100,21)
    for rh in np.linspace(0.1,1,10):
        plt.plot(ts, humidity_ratio(rh, ts), 'k')
    plt.xlabel('Temperature [degF]')
    plt.ylabel('Humidity Ratio')
    plt.ylim(0,0.02)
    plt.xlim(0,90)
    # RH labels on right hand side
    ax1 = plt.axes()
    ax2 = ax1.twinx()
    ax2.get_yaxis().set_major_locator(ticker.FixedLocator(humidity_ratio(np.linspace(0,1,11), 90)/0.020)) # TODO don't hardcode limits
    ax2.get_yaxis().set_major_formatter(ticker.FixedFormatter(np.linspace(0,100,11)))
    plt.ylabel('Indoor RH [%]')
    return ax1
