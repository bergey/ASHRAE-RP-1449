#!/usr/bin/python
import datetime as dt
import sys
import csv
from os.path import exists, join, basename
import numpy as np
from glob import glob
import re
import shutil
import platform
graphs = platform.system() == 'Linux'
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
    return [int(match.group(k)) for k in ['s', 'z', 'h', 'v', 'rh']] + [desc]
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

def output_row(desc, f, hourly, out_csv, first_run=False):
    h, sum_vals = f(**hourly)
    if first_run: 
        # first row of output
        out_csv.writerow( parse_name(None) + h )
    out_csv.writerow(desc + sum_vals)

def summarize_csv(specs):
  first_run = True
  general_csv = output_handle('summary')
  rh_csv = output_handle('rh-thresholds')
  for desc, scenario_path in specs:
    name = desc[-1]
    if exists(scenario_path):
        print "loading {0} from {1}".format(name, scenario_path)
        hourly = hourly_data(scenario_path)
        print "summarizing {0}".format(name)
        output_row(desc, summarize_run, hourly, general_csv, first_run)
        output_row(desc, rh_stats, hourly, rh_csv, first_run)
        first_run = False # flag, never becomes true again in this call
        if graphs:
            print "graphing {0}".format(name)
            plot_TRH(name, hourly)
            plot_Wrt(name, hourly)
            plot_rh_hist(name, hourly)
            plot_t_hist(name, hourly)
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
def summarize_run(RHi, Ti, C_i, Qsac, Qlac, ACKW, RTFc, RTFe, RTFh, RTFrh, RTFacf, RTFd, RTFdf, rtfvf, rtfxf, rtfhf, KWHT, FANKW, DKW, DFANKW, KWVF, KWXF, KWHF, ACH, **hourly):
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
      'cooling': (ACKW * RTFc).sum(),      # AC Electric Use (kWh)
      'heating': (KWHT * RTFh).sum(),      # Heater Electric Use (kWh)
      'AHU': (RTFacf * FANKW).sum(),       # Supply Fan Electric Use (kWh)
      'dehumidifier': (RTFd * DKW).sum(),  # Des Unit Electric Use (kWh)
      'DH fan': (RTFdf * DFANKW).sum(),    # Des FAN Electric Use (kWh)
      'vent damper': (rtfvf * KWVF).sum(), # Vent Damp/Fan Electric Use (kWh)
      'exhaust fan': (rtfxf * KWXF).sum(),     # Exhaust Fan Electric Use (kWh)
      'HRV': (rtfhf * KWHF).sum(),         # HRV Electric Use (kWh)
    }

# submetered energy consumption
    for key, value in annual_kWh.iteritems():
      heads.append('annual {0} kWh'.format(key))
      vals.append(value)

    heads.append('AHU Fan energy for Cooling')
    vals.append( (RTFc * FANKW).sum() )

    heads.append('AHU Fan energy for Heating')
    vals.append( (RTFh * FANKW).sum() )

    heads.append('AHU fan energy for Ventilation and Mixing')
    vals.append( ( (RTFacf - RTFc - RTFh) * FANKW ).sum() )

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

def concat(lst):
  ret = []
  for l in lst:
    ret += l
  return ret

def output_handle(name):
  output_path = dt.datetime.now().strftime('%Y-%m-%d-%H%M-{0}.csv'.format(name))
  file = open(output_path, 'wb')
  return csv.writer(file)

if __name__ == '__main__':
  if len(sys.argv) >= 3 and exists(sys.argv[1]) and exists(sys.argv[2]):
    data_path = sys.argv[1]
    specs = concat( [ collect_specs(c, data_path) for c in sys.argv[2:] ] )
    specs.sort()
    summarize_csv( specs )
  else:
    print """{0} DATAPATH SPEC...
    look in DATAPATH for data files (for_##.dat)
    look in SPEC for descriptions of each run

    {0} expects the data files to be in arranged hierarchically.
    It expects one directory in DATAPATH for each SPEC listed on the command
    line, having the same name as SPEC without the .csv extension.
    Within each directory, there should be one folder named Run# for each line
    in SPEC.  Each Run# directory should have all for_##.dat files for that run.
    """
