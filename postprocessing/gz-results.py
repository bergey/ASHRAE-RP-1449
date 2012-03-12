#!/usr/bin/env python
# zip (or unzip) every regular file in a given directory tree

from os import listdir, system
from os.path import isdir, join
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-q', '--quiet', help='only report errors', dest='verbose', action='store_false', default=True)
parser.add_option('-u', '--unzip', action='store_true', help='unzip encountered gz files', dest='unzip', default=False)

(options, args) = parser.parse_args()

def already_zip(p):
    if p[-2:] in ['gz'] or p[-3:] in ['bz2', 'zip']:
        return True
    else:
        return False

paths = [d for d in args if isdir(d)]
while paths:
    wd = paths.pop(0)
    for name in listdir(wd):
        p = join(wd, name)
        if isdir(p):
            paths.append(p)
        elif already_zip(p) ^ options.unzip:
            if options.verbose:
                print('skipping {0}'.format(p))
            continue
        else:
            if options.unzip:
                cmd = 'gunzip {0}'.format(p)
            else:
                cmd = 'gzip {0}'.format(p)
            if options.verbose:
                print(cmd)
            system(cmd)
