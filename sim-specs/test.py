#!/usr/bin/env python3
from glob import glob
import csv
from os.path import join, basename

def line_count(old, new):
    if old != new:
        return 1
    else:
        return 0

def diff_cols(old, new):
    cols = []
    for key, value in old.items():
        if new[key] != value:
            print("{0} differ in {1}: was {2} is {3}".format(old['Desc'], key, value, new[key]))
            cols += key
    return cols

def same_keys(old, new):
    old_scenarios = set(old.keys())
    new_scenarios = set(new.keys())
    if not old_scenarios.issubset(new_scenarios):
        print("{0} removed these scenarios:".format(nname))
        print("  {0}".format('\n  '.join(old_scenarios.difference(new_scenarios))))
    if not new_scenarios.issubset(old_scenarios):
        print("{0} added these scenarios:".format(nname))
        print("  {0}".format('\n  '.join(new_scenarios.difference(old_scenarios))))

def keyindex(itr, key):
    return dict([(item[key], item) for item in itr])

for oname in glob("regr-base/*"):
        nname = basename(oname)
        print(nname)
        cold = csv.DictReader(open(oname))
        cnew = csv.DictReader(open(nname))
        new = keyindex(cnew, 'Desc')
        old = keyindex(cold, 'Desc')
        same_keys(old, new)
        for scenario in old.keys():
            diff_cols(old[scenario], new[scenario])
