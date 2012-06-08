#!/usr/bin/python0
import datetime as dt
import sys
import csv
from os.path import exists, join, basename
import numpy as np
from glob import glob
import re
import shutil
import platform
from parametrics import hourly_data, daily_total, daily_mean
#graphs = platform.system() == 'Linux'
graphs = False
if graphs:
    from graphs import *

descre = re.compile(r'z(?P<z>\d)h(?P<h>\d+)s(?P<s>\d+)rh(?P<rh>\d+)v(?P<v>\d)')

# TODO rewrite comments as docstrings

# the plan:
# take csv, path on cli
# fordat to take a file and return a dict of hourly lists
# dict_of_results to collect all of the output data for a specified run
# process to take the simulation outputs and return a new dict with summaries
# one function to save the output
# alternate function to save output as one line per run

# take a file and return a dict of hourly lists
# handle is a file handle to a tab-separated file 
# with column names in the first row
# fordat returns a dictionary with keys from the first row and a numpy array of numbers per key

def parse_name(scenario):
  """Parse name and return value of each key"""
  if not scenario:
# return the header that matches the order of the fields returned below
    return [ 'System', 'Climate Zone', 'HERS Level', 'Ventilation System', 'RH Setpoint', 'Description' ]
  desc = scenario['Desc']
  match = descre.search(desc)
  if match:
    return [int(match.group(k)) for k in ['s', 'z', 'h', 'v', 'rh']] + [desc]
  else:
    raise RuntimeError('Cannot interpret scenario name {0}'.format(scenario))


def collect_specs(spec_path, data_path):
  def scenario_path(s):
    return join(data_path, basename(spec_path)[:-4], s['Desc'])
# open the csv from gensim, and parse some useful things out of it
  spec_file = open(spec_path)
  spec = csv.DictReader(spec_file)
# turn each row of csv into a tuple: name and path to data
# the field order in name determines sort order
  return [(parse_name(s), scenario_path(s)) for s in spec]

def output_row(desc, f, hourly, out_csv, first_run=False):
    try:
        hr, sum_vals = f(**hourly.__dict__)
        if first_run: 
            # first row of output
            out_csv.writerow( parse_name(None) + hr )
        out_csv.writerow(desc + sum_vals)
    except TypeError as e:
        print "Not enough data for {1}; skipping: {0}".format(desc, f.__name__)
        print(len(hourly.__dict__.keys()))
        print(hourly.__dict__.keys())
        raise e

def summarize_csv(specs):
  first_run = True
  general_csv = output_handle('summary')
  rh_csv = output_handle('rh-thresholds')
  check_csv = output_handle('checking')
  rh_by_runtime_csv = output_handle('daily-rh-runtime')
  for desc, scenario_path in specs:
    name = desc[-1]
    if exists(scenario_path):
        print("loading {0} from {1}".format(name, scenario_path))
        hourly = hourly_data(scenario_path)
        duration = len(hourly.TIME)
        if duration  != 8760:
            print("skipping {0}: {1} hours of data instead of 8760".format(name, duration))
            continue
        print("summarizing {0}".format(name))
        output_row(desc, summarize_run, hourly, general_csv, first_run)
        output_row(desc, rh_stats, hourly, rh_csv, first_run)
        output_row(desc, check_loads, hourly, check_csv, first_run)
        output_row(desc, rh_by_runtime, hourly, rh_by_runtime_csv, first_run)
        for k in ['SOLN', 'SOLE', 'SOLS', 'SOLW', 'QWALLS', 'QCEIL', 'QFLR', ]:
            if not hasattr(hourly, k):
                print("missing {0}".format(k))
        first_run = False # flag, never becomes true again in this call
        if graphs:
            print("graphing {0}".format(name))
            plot_TRH(hourly, name)
            plot_humidity_ratio(hourly, name)
            #plot_Wrt(name, hourly)
            plot_rh_hist_daily(hourly, name)
            #plot_t_hist(name, hourly)
            plot_daily_psychrometric(hourly, name)
            ac_bal_point(hourly, name)
    else:
# scenario path does not exist
        print( "skipping {0}: path {1} does not exist".format(name, scenario_path))

def contiguous_regions(condition):
    """Finds contiguous True regions of the boolean array "condition". Returns
    a 2D array where the first column is the start index of the region and the
    second column is the end index."""

    # Find the indicies of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero() 

    # We need to start things after the change in "condition". Therefore, 
    # we'll shift the index by 1 to the right.
    idx += 1

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size - 1]

    # Reshape the result into two columns
    idx.shape = (-1,2)
    return idx

def long_events(condition, length):
    bounds = contiguous_regions(condition)
    return (bounds[:,1] - bounds[:,0] >= length).sum()
  #count = 0
  #for start, stop in contiguous_regions(condition):
    #if stop - start >= length:
      #count += 1
  #return count

def rh_above_threshold(threshold, RHi):
    i = np.where(RHi > threshold, 1, 0)
    heads = ['hours above {0}% RH'.format(threshold)]
    vals = [i.sum()]

# RH events over 4, 8 hours
    heads.append('RH events {0}% for 4+ hours'.format(threshold))
    vals.append( long_events(RHi > threshold, 4) )
    heads.append('RH events {0}% for 8+ hours'.format(threshold))
    vals.append( long_events(RHi > threshold, 8) )

    return (heads, vals)

def check_loads(SOLN, SOLE, SOLS, SOLW, QWALLS, QCEIL, QFLR, **hourly):
    ret = [ ( 'Window Gain North', SOLN.sum() ),
            ( 'Window Gain East',  SOLE.sum() ),
            ( 'Window Gain South', SOLS.sum() ),
            ( 'Window Gain West',  SOLW.sum() ),
            ( 'Total Wall Gain', QWALLS.sum() ),
            ( 'Ceiling Gain',     QCEIL.sum() ),
            ( 'Floor Gain',        QFLR.sum() ),
          ]
    return map(list, zip(*ret))

def rh_stats(RHi, **hourly):
    heads = ['mean RH']
    vals = [RHi.mean()]

    heads.append('max RH')
    vals.append(RHi.max())

    for threshold in [50, 55, 60, 65]:
      h, v = rh_above_threshold(threshold, RHi)
      heads.extend(h)
      vals.extend(v)

    return (heads, vals)
    

# take the simulation outputs and summarize
# return a pair: headings in order, value list in matching order
def summarize_run(RHi, Ti, C_i, Qsac, Qlac, ACKW, RTFc, RTFe, RTFh, RTFrh, RTFacf, RTFd, RTFdf, rtfvf, rtfxf, rtfhf, KWHT, FANKW, DKW, DFANKW, KWVF, KWXF, KWHF, ACH, **hourly):#FANKW_c, FANKW_h, FANKW_v, **hourly):
    heads = []
    vals = []

    # Overall RH Data
    heads.append('mean RH')
    vals.append(RHi.mean())

    heads.append('max RH')
    vals.append(RHi.max())

    h, v = rh_above_threshold(60, RHi)
    heads.extend(h)
    vals.extend(v)


# Temperature 
    heads.append('average T')
    vals.append(Ti.mean())

    heads.append('max T')
    vals.append(Ti.max())

    heads.append('min T')
    vals.append(Ti.min())

    heads.append('hours below 67.5F')
    vals.append( np.where(Ti < 67.5, 1, 0).sum() )

    heads.append('hours below 67F')
    vals.append( np.where(Ti < 67, 1, 0).sum() )

    heads.append('hours above 78.5F')
    vals.append( np.where(Ti > 78.5, 1, 0).sum() )

    heads.append('hours above 79F')
    vals.append( np.where(Ti > 79, 1, 0).sum() )

# CO2
    heads.append('max CO2')
    vals.append( C_i.max() * 1e6 )
    
    # AC SHR and EER
    heads.append('AC Sensible Fraction')
    ac_btu_yr = ((Qsac).sum() + (Qlac).sum())
    if ac_btu_yr == 0:
      vals.append('No cooling')
    else:
      vals.append( (Qsac).sum() /  ac_btu_yr )

    heads.append('Annual Avg EER')
    ac_kwh_yr = ACKW.sum()
    if ac_kwh_yr == 0:
      vals.append('No kWh')
    else:
      vals.append( ac_btu_yr / ac_kwh_yr / 1e3 )
    
    # Various Runtimes

    vals += [
        RTFc.max(),     # Max hourly fraction
        RTFh.max(),     # Max hourly fraction
        RTFc.sum(),     # AC Runtime
        RTFe.sum(),     # Econ Runtime
        RTFh.sum(),     # Heating Runtime
        RTFrh.sum(),    # ReHeat Runtime
        RTFacf.sum(),   # Supply Fan Runtime
        RTFacf.sum() - RTFc.sum() - RTFh.sum(), # AHU for vent & mixing
        RTFd.sum(),     # Dehumid Runtime
        RTFdf.sum(),    # Des Fan Runtime
        rtfvf.sum(),    # Vent Damper / Fan Runtime
        rtfxf.sum(),    # Exhaust Fan Runtime
        rtfhf.sum(),    # HRV Runtime
        ]

    heads += [
      'Max Cooling in One Hour',
      'Max Heating in One Hour',
      'AC Runtime',
      'Econ Runtime',
      'Heating Runtime',
      'ReHeat Runtime',
      'AHU Fan Runtime',
      'AHU Runtime for vent & mixing',
      'Dehumid Runtime',
      'Des Fan Runtime',
      'Vent Damper / Fan Runtime',
      'Exhaust Fan Runtime',
      'HRV Runtime' ]

# Don't bother reporting Qrh; RTFrh should be 0
    annual_kWh = {
      'cooling': ACKW.sum(),      # AC Electric Use (kWh)
      'heating': KWHT.sum(),      # Heater Electric Use (kWh)
      'AHU': FANKW.sum(),       # Supply Fan Electric Use (kWh)
      'dehumidifier': DKW.sum(),  # Des Unit Electric Use (kWh)
      'DH fan': DFANKW.sum(),    # Des FAN Electric Use (kWh)
      'vent damper': KWVF.sum(), # Vent Damp/Fan Electric Use (kWh)
      'exhaust fan': KWXF.sum(),     # Exhaust Fan Electric Use (kWh)
      'HRV': KWHF.sum(),         # HRV Electric Use (kWh)
    }

# submetered energy consumption
    for key, value in annual_kWh.items():
      heads.append('annual {0} kWh'.format(key))
      vals.append(value)

    if 'FANKW_c' in hourly.__dict__.keys():
        # temporary hack transitioning from TRD without these values
        FANKW_c = hourly['FANKW_c']
        FANKW_h = hourly['FANKW_h']
        FANKW_v = hourly['FANKW_v']

        # New versions multiplying by runtime at each timestep, in TRD
        heads.append('AHU Fan energy for Cooling')
        vals.append( FANKW_c.sum() )

        heads.append('AHU Fan energy for Heating')
        vals.append( FANKW_h.sum() )

        heads.append('AHU fan energy for Ventilation and Mixing')
        vals.append( FANKW_v.sum() )

# Infiltration --- mechanical and natural
    heads.append('Lowest Infiltration in one hour')
    vals.append(ACH.min())

    heads.append('Mean Infiltration')
    vals.append(ACH.mean())

    heads.append('Highest Infiltration in one hour')
    vals.append(ACH.max())

# Total energy consumption
    heads.append('Total annual kWh')
    vals.append(sum(annual_kWh.values()))

    return (heads, vals)

def rh_by_runtime(RTFc, RTFh, RHi, **hourly):
    heads = ['Hours above 50% RH; days with no cooling or heating',
             'Number of days; no cooling or heating',
             'Mean RH, days with no cooling or heating',
             'Hours above 50% RH; days with cooling, no heating',
             'Number of days;  cooling, no heating',
             'Mean RH, days with cooling, no heating',
             'Hours above 50% RH; days with heating, no cooling',
             'Number of days; heating, no cooling',
             'Mean RH, days with heating, no cooling',
             'Hours above 50% RH; days with heating and cooling',
             'Number of days; heating and cooling',
             'Mean RH, days with heating and cooling']
    vals = []
    conditions = [np.intersect1d(np.where(daily_total(RTFc)==0)[0], np.where(daily_total(RTFh)==0)[0]),
                  np.intersect1d(np.where(daily_total(RTFc)>0)[0], np.where(daily_total(RTFh)==0)[0]),
                  np.intersect1d(np.where(daily_total(RTFc)==0)[0], np.where(daily_total(RTFh)>0)[0]),
                  np.intersect1d(np.where(daily_total(RTFc)>0)[0], np.where(daily_total(RTFh)>0)[0])]
    for condition in conditions:
        vals.append(daily_total(np.where(RHi > 50, 1, 0))[condition].sum())
        vals.append(len(condition))
        vals.append(daily_mean(RHi)[condition].mean())
    if len(heads) != len(vals):
        print("only {0} values for {1}".format(len(vals), hourly['name']))
    return (heads, vals)

def concat(lst):
  ret = []
  for l in lst:
    ret += l
  return ret

def output_handle(name):
  output_path = dt.datetime.now().strftime('summary/%Y-%m-%d-%H%M-{0}.csv'.format(name))
  file = open(output_path, 'wb')
  return csv.writer(file)

if __name__ == '__main__':
  if len(sys.argv) >= 3 and exists(sys.argv[1]) and exists(sys.argv[2]):
    data_path = sys.argv[1]
    specs = concat( [ collect_specs(c, data_path) for c in sys.argv[2:] ] )
    specs.sort()
    summarize_csv( specs )
  else:
    print("""{0} DATAPATH SPEC...
    look in DATAPATH for data files (for_##.dat)
    look in SPEC for descriptions of each run

    {0} expects the data files to be in arranged hierarchically.
    It expects one directory in DATAPATH for each SPEC listed on the command
    line, having the same name as SPEC without the .csv extension.
    Within each directory, there should be one folder named Run# for each line
    in SPEC.  Each Run# directory should have all for_##.dat files for that run.
    """)
