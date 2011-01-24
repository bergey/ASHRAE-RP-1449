#!/usr/bin/python
import datetime as dt
import sys
import csv
from os.path import exists, join, basename
import numpy as np
from glob import glob
import re
from graphs import *
import shutil

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
def fordat(filename):
# Open the file, read the first line, close the file
# This is ugly; the commented out code would be nicer, but genfromtxt isn't reading names on Ubuntu
    handle = open(filename)
    head = handle.next().split()
    handle.close()
    handle = open(filename)

    arr = np.genfromtxt(handle, names=True)
    ret = dict()
    #for n in arr.dtype.names:
        #ret[n] = arr[n]
    for i, n in enumerate(head):
        ret[n] = arr[:,i]
    return ret

# collect all of the output data for a specified run
# returns 
# path should be a directory with several for_*.dat files
def hourly_data(path):
  ret = dict()
  for filename in glob(join(path, "for_*.dat")):
    #handle = open(filename)
    ret.update(fordat(filename))
  return ret

def parse_name(scenario):
  """Parse name and return value of each key"""
  if not scenario:
# return the header that matches the order of the fields returned below
    return [ 'System', 'Climate Zone', 'HERS Level', 'Ventilation System', 'RH Setpoint', 'Description' ]
  desc = scenario['Desc']
  match = descre.search(desc)
  if match:
    return [match.group(k) for k in ['s', 'z', 'h', 'v', 'rh']] + [desc]
  else:
    raise RuntimeError('Cannot interpret scenario name {0}'.format(scenario))


def collect_specs(spec_path, data_path):
  def scenario_path(s):
    return join(data_path, basename(spec_path)[:-4], 'Run{0}'.format(s['Run']))
# open the csv from gensim, and parse some useful things out of it
  spec_file = open(spec_path)
  spec = csv.DictReader(spec_file)
# turn each row of csv into a tuple: name and path to data
# the field order in name determines sort order
  return [(parse_name(s), scenario_path(s)) for s in spec]

def summarize_csv(specs, out_csv):
  for desc, scenario_path in specs:
    name = desc[-1]
    if exists(scenario_path):
        print "loading {0} from {1}".format(name, scenario_path)
        hourly = hourly_data(scenario_path)
        print "summarizing {0}".format(name)
        h, sum_vals = summarize_run(**hourly)
        print "graphing {0}".format(name)
        plot_TRH(name, hourly)
        plot_Wrt(name, hourly)
        plot_rh_hist(name, hourly)
        plot_t_hist(name, hourly)
        if not head: 
          # first row of output
            head = parse_name(None) + h # save head from first scenario
            out_csv.writerow(head)
        out_csv.writerow(desc + sum_vals)
    else:
# scenario path does not exist
        print "skipping {0}: path {1} does not exist".format(name, scenario_path)

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
  count = 0
  for start, stop in contiguous_regions(condition):
    if stop - start > length:
      count += 1
  return count

# take the simulation outputs and summarize
# return a pair: headings in order, value list in matching order
def summarize_run(RHi, Ti, C_i, Qsac, Qlac, ACKW, RTFc, RTFe, RTFh, RTFrh, RTFacf, RTFd, RTFdf, rtfvf, rtfxf, rtfhf, **hourly):
    heads = []
    vals = []

    # Overall RH Data
    i = np.where(RHi > 60, 1, 0)
    heads.append('mean RH')
    vals.append(RHi.mean())

    heads.append('hours above 60% RH')
    vals.append(i.sum())

    heads.append('max RH')
    vals.append(RHi.max())
    
# RH events over 4, 8 hours
    heads.append('RH events 60% for 4+ hours')
    vals.append( long_events(RHi > 60, 4) )
    heads.append('RH events 60% for 8+ hours')
    vals.append( long_events(RHi > 60, 8) )

    heads.append('average T')
    vals.append(Ti.mean())

    heads.append('max T')
    vals.append(Ti.max())

    heads.append('min T')
    vals.append(Ti.min())

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
    ac_kwh_yr = (ACKW * RTFc).sum()
    if ac_kwh_yr == 0:
      vals.append('No kWh')
    else:
      vals.append( ac_btu_yr / ac_kwh_yr / 1e3 )
    
    # Various Runtimes
    runtimes = ['RTFc', 'RTFe', 'RTFh', 'RTFrh', 'RTFacf', 'RTFd', 'RTFdf', 'rtfvf',
            'rtfxf', 'rtfhf']
    for v in runtimes: 
      if not v in locals():
            print "Missing {0}".format(v)
           # exec v + ' = asarray([0.])'

    vals += [
        RTFc.sum(),     # AC Runtime
        RTFc.max(),     # Max hourly fraction
        RTFe.sum(),     # Econ Runtime
        RTFh.sum(),     # Heating Runtime
        RTFrh.sum(),    # ReHeat Runtime
        RTFacf.sum(),   # Supply Fan Runtime
        RTFd.sum(),     # Dehumid Runtime
        RTFdf.sum(),    # Des Fan Runtime
        rtfvf.sum(),    # Vent Damper / Fan Runtime
        rtfxf.sum(),    # Exhaust Fan Runtime
        rtfhf.sum(),    # HRV Runtime
        ]

    heads += [
      'AC Runtime',
      'Max Cooling in One Hour',
      'Econ Runtime',
      'Heating Runtime',
      'ReHeat Runtime',
      'AHU Fan Runtime',
      'Dehumid Runtime',
      'Des Fan Runtime',
      'Vent Damper / Fan Runtime',
      'Exhaust Fan Runtime',
      'HRV Runtime' ]

# Total energy consumption
    annual_kWh = [
        (ACKW * RTFc).sum(),                 # AC Electric Use (kWh)
        (KWHT * RTFh).sum(),                 # Heater Electric Use (kWh)
        (RTFacf * FANKW).sum(),              # Supply Fan Electric Use (kWh)
        (RTFd * DKW).sum(),                  # Des Unit Electric Use (kWh)
        (RTFdf * DFANKW).sum(),              # Des FAN Electric Use (kWh)
        (rtfvf * KWVF).sum(),                # Vent Damp/Fan Electric Use (kWh)
        (rtfxf * KWXF).sum(),                # Exhaust Fan Electric Use (kWh)
        (rtfhf * KWHF).sum(),                # HRV Electric Use (kWh)
    ]
    heads.append('Annual kWh (HVAC)')
    vals.append( annual_kWh.sum() )

    #fmt_str = ','.join(['%.1f' for each in l]) + ','
    #f.write(fmt_str % tuple(l))

    return (heads, vals)

def concat(lst):
  ret = []
  for l in lst:
    ret += l
  return ret

def output_handle( ):
  output_path = dt.datetime.now().strftime('%Y-%m-%d-%H:%M-summary.csv')
  file = open(output_path, 'wb')
  return csv.writer(file)

if __name__ == '__main__':
  print sys.argv
  if len(sys.argv) >= 3 and exists(sys.argv[1]) and exists(sys.argv[2]):
    data_path = sys.argv[1]
    out_file = output_handle()
    specs = concat( [ collect_specs(c) for c in sys.argv[2:] ] )
    specs.sort()
    summarize_csv( specs, out_file )
  else:
    print """No usage summary yet; read the code"""
