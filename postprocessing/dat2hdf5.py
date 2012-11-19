from pandas import *
from parametrics import hourly_data
import os
from os.path import join, isdir
from numpy import arange

DIR = '/home/bergey/Library/rp-1449-results/'

dates = arange(1,8761)

for system in os.listdir(DIR):
    store = HDFStore('{0}.h5'.format(system))
    n = len(os.listdir(join(DIR,system)))-1
    i = 0
    print("entering directory {0}".format(system))
    for sim in os.listdir(join(DIR,system)):
        if not isdir(join(DIR,system, sim)):
            continue
        i += 1
        print("{0}/{1}: {2}".format(i,n,sim))
        h = hourly_data(join(DIR,system,sim))
        df = DataFrame(h.__dict__, index=dates)
        store[sim] = df
