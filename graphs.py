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

def plot_rh_hist(name, hourly):
    fig = plt.figure()
    plt.hist(hourly['RHi'],50)
    plt.xlabel('percent RH')
    plt.ylabel('Number of Hours')
    plt.title('{0}: Indoor RH Histogram'.format(name))
    fig.savefig( '{0}-rh-histogram.png'.format(name) )
