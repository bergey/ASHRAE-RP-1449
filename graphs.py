# coding= utf-8
import numpy as np
import matplotlib.pyplot as plt

def plot_TRH(name, hourly):
    fig = plt.figure()
    line_ti, = plt.plot(hourly['Ti'])
    line_ti.set_linewidth(0.2)
    ax1, = fig.axes
    ax1.axis([0,8760,20,95])
    line_to, = plt.plot(hourly['To'])
    line_to.set_linewidth(0.2)
    plt.ylabel('degrees F')
    plt.xlabel('Hour of Year')
    ax2 = ax1.twinx()
    line_rhi, = ax2.plot(hourly['RHi'], label='Indoor RH', linewidth=0.2, color='r')
    plt.legend([line_to, line_ti, line_rhi], ['Outdoor T', 'Indoor T', 'Indoor RH'], loc='lower right')
    plt.axes(ax2)
    plt.ylabel('percent RH')
    ax2.axis([0,8760,0,100])
    plt.title('{0}: Annual Conditions'.format(name))
    #plt.show()
    fig.savefig( '{0}-annual-trh.png'.format(name) )
    plt.close()

def plot_Wrt(name, hourly):
    fig = plt.figure()
    line_Wi, = plt.plot(hourly['Wi'], linewidth=0.2)
    line_Wo, = plt.plot(hourly['Wo'], linewidth=0.2)
    plt.ylabel('water content of air (by mass)')
    plt.xlabel('Hour of Year')
    ax1, = fig.axes
    ax2 = ax1.twinx()
    plt.axes(ax2)
    line_RTFc, = plt.plot(hourly['RTFc'], linewidth=0.2, color='r')
    ax2.axis([0,8760,-0.5,2.5])
    plt.ylabel('Fraction of Hour')
    plt.legend([line_Wo, line_Wi, line_RTFc], ['Outdoor W', 'Indoor W', 'Cooling Runtime'], loc='upper left')
    plt.title('{0}: Moisture Removal'.format(name))
    fig.savefig('{0}-annual-moisture.png'.format(name))
    plt.close()

def plot_rh_hist(name, hourly):
    fig = plt.figure()
    plt.hist(hourly['RHi'],50)
    plt.xlabel('percent RH')
    plt.ylabel('Number of Hours')
    plt.title('{0}: Indoor RH Histogram'.format(name))
    fig.savefig( '{0}-rh-histogram.png'.format(name) )
    plt.close()

def plot_t_hist(name, hourly):
    fig = plt.figure()
    plt.hist(hourly['Ti'],50)
    plt.xlabel('degrees F')
    plt.ylabel('Number of Hours')
    plt.title('{0}: Indoor T Histogram'.format(name))
    fig.savefig( '{0}-ti-histogram.png'.format(name) )
    plt.close()

def plot_AC_balance(name, hourly):
    fig = plt.figure()
    plt.scatter(hourly['To'], hourly['RTFc'] * hourly['ACKW'], marker='+', s=10, linewidths=0.1, color='r')
    plt.xlabel('Outdoor T (degrees F)')
    plt.ylabel('kW cooling')
    plt.title('{0}: Cooling Balance'.format(name))
    fig.savefig( '{0}-AC-balance.png'.format(name) )
    plt.close()

def plot_AC_hist(name, hourly):
    fig = plt.figure()
    xs = np.linspace(60,110,51)
    cooling = np.where(hourly['RTFc'] >= 0.05, 1, 0)
    ys = []
    for low, high in zip(xs, xs[1:]):
        in_bin = np.where( (hourly['To']>=low) & (hourly['To']<high) )
        ys.append( cooling[in_bin].sum() )
    ys.append( np.where( hourly['To'] >= xs[-1], cooling, 0).sum() )
    plt.bar(xs, ys, width=1)
    plt.xlabel('Outdoor T (degrees F)') # TODO why doesn't unicode ° render in png graph?
    plt.ylabel('Hours with at least 3 minutes Cooling')
    plt.title( '{0}: Cooling Hours Breakdown'.format(name) )
    fig.savefig( '{0}-AC_hist'.format(name) )
    plt.close()

month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', ]

def by_month(hours):
    splits = [32,60,91,121,152,182,213,244,274,305,335]
    by_day = hours.reshape(365, 24) # throw error if not 8760 long
    return np.array_split(by_day, splits, axis=0)

def plot_window_gain(name, hourly):
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
        fig.savefig('{0}-by-month.png'.format(name))
        plt.close()
    try:
        for key in ['SOLS', 'SOLE', 'SOLN', 'SOLW']:
            helper('{0}-{1}'.format(name, key), hourly[key])
    except KeyError:
        print "Not enough data for plot_window_gain; skipping: {0}".format(name)
