# Counts hours above and below setpoint
# reports to csv file

import sys
from os.path import join, exists
import csv
from subprocess import check_call

prefix = '/cygdrive/f/' # change this if not using Cygwin

def pretty_loc(tmy):
	return 

if len(sys.argv) < 2:
	die("%s takes at least one argument: directory with results to be processed" % sys.argv[0])

ofile = open('gnuplot-input', 'w')
ofile.write("""set terminal pdf
set xrange [-40:120]
set yrange [40:80]
set xlabel 'degrees F'
set ylabel 'degrees F'
""")

# iterate over folders named in input
for simset in sys.argv[1:]:
	summary = csv.DictReader(open(join(prefix,simset,'SimRuns.csv'))) # should probably handle errors here
	
	# iterate over files in parametric run
	for runline in summary:
		if not exists(join(prefix,simset,'Run%s'%runline['Run'],'For_21.dat')):
			# Parametric run was interupted
			# This is much less likely with the python batch manager
			print("\t********\nStopping after Run %s\n\t********" % (i-1))
			break
			
		datafile = join(simset,"Run%s" % runline['Run'],"for_21.dat")
		location = runline['WeatherFile'].replace('_',' ').replace('-',', ')
		output = "%s-%03d.pdf" % (simset, int(runline['Run']))
		print location
		print output

#		ofile.write("""set output '%s'
#set title 'Run %s: %s'
#plot '%s' using 1:2 title 'Outdoor' lc 0 pt 0, '%s' using 1:4 title 'Indoor'
#
#""" % (output, runline['Run'], location, datafile, datafile))
		ofile.write("""set output '%s'
set title 'Run %s: %s'
plot '%s' using 2:4 title 'Temp' 
""" % (output, runline['Run'], location, datafile))


			
ofile.close()
check_call(['gnuplot', 'gnuplot-input'])
