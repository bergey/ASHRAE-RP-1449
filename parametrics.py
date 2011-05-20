# library of utility functions for analyzing and graphing large datasets
# much of this is specific to TRNSYS output
from os.path import join, isdir
import numpy as np
from glob import glob

def fordat(filename):
# Open the file, read the first line, close the file
# This is ugly; the commented out code would be nicer, but genfromtxt isn't reading names on Ubuntu
    handle = open(filename)
    head = handle.next().split()
    handle.close()
    handle = open(filename)

    arr = np.loadtxt(handle, skiprows=1) # test using loadtxt instead of genfromtxt
    ret = dict()
    #for n in arr.dtype.names:
        #ret[n] = arr[n]
    for i, n in enumerate(head):
        ret[n] = arr[:,i]
    return ret

# collect all of the output data for a specified run
# returns dict of 1D numpy arrays
# path should be a directory with several for_*.dat files
def hourly_data(path):
  ret = dict()
  for filename in glob(join(path, "for_*.dat")):
    #handle = open(filename)
    ret.update(fordat(filename))
  return ret

month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', ]
short_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

def by_month(hours):
    splits = [31,59,90,120,151,181,212,243,273,304,334]
    by_day = hours.reshape(365, 24) # throw error if not 8760 long
    return np.array_split(by_day, splits, axis=0)

#support function for scenarios, below
def get_keys(names):
    ks = zip(*names)
    for axis in ks:
        if len(axis)==1:
            continue
        else:
            chars = [re.match(r'\D+').group(0) for k in axis]
            if not all(array(chars[1:])==chars[0]):
                raise ValueError("Naming convention is inconsistent")
            else:
                ret.append((chars[0], [re.match(r'\d+').group(0) for k in axis]))

def scenarios(path):
# call hourly_dict on all scenarios in path
# return n-dimensional list of lists based on scenario name
    names = [re.findall(r'\D+\d+', s) for s in os.listdir(path) if isdir(join(path, s))]
    keys = map(set,zip(*names))
