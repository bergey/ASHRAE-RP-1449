This README should explain how all of these files work 

*TRNSYS* reads a *TRD* file, along with some supporting files, and
writes hourly data to several *for_##.dat* files.  The TRD has
equations and connections between *Components*, which are written in
Fortran and compiled seperately.  Everything else here either produces
inputs to TRNSYS or processes the outputs.

# buildings

The *buildings* directory has files which describe the building
dimensions and enclosure materials to TRNSYS.  TRNSYS Type56 reads
these files and models thermal and moisture loads.  There is one set
of files for each combination of HERS level (ie, energy efficiency),
climate zone, and building size.  The *.bui* files can be edited using
TRNBuild.exe or as text files.  The *.bld*, *.inf*, and *.trn* files
are created by TRNBuild.exe when saving a .bui file.
*Single_Zone_Buildings.txt* is a lookup file used to associate a
given TRD with a given building file.

# TRN_Resdh4.py

*TRN_Resdh4.py* takes an input TRD file, changes some variables within
it, and calls TRNSYS on the output file.  In its --batch mode, it
reads a CSV file specifying source TRD, variable names, and values,
and calls TRNSYS once per line in the CSV file.  --batch mode will
also accept multiple CSV files.  TRN_Resdh4.py will place the outputs
of each CSV file in a directory named after that CSV file.  For
example,

> python TRN_Resdh4.py --batch sim-specs/s1.csv

will create a directory `s1` with a subdirectory for each row in *s1.csv*.

> python TRN_Resdh4.py --batch sim-specs/s1.csv sim-specs/s2.csv

will create two directories, `s1` and `s2`.

For this project, all scenarios use 1449.TRD as the source file.  All
differences between scenarios are expressed in the CSV files.
Examples include:

- TMY weather file (building location)
- building file (enclosure specification)
- AC capacity (tons)
- dehumidification system (affects many variables)
- RH setpoint

More information about the CSV file format which TRN_Resdh4 uses is
given in the [sim-specs](#sim-specs) section.


# <a id="sim-specs"> sim-specs </a>

The CSV files are kept in the *sim-specs/* directory (short for
simulation specifications).  *TRN_Resdh4.py* expects one row per
scenario, and one column per variable.  The variable names are taken
from the first row of the CSV.  The script gensim.py (also in
sim-specs/) generates the CSV files.  

Each scenario is described by 5 values, and these are combined into a
compact name of the form z#h#s#rh#v#-# where each # is replaced by a
number (except the last).  The fields are:

- z: Climate Zone (0-5) (as a special case, 0 refers to Orlando, FL)
- h: HERS level, (50-130) a proxy for performance of enclosure and mechanical systems
- s: system, refering to the dehumidification systems enumerated in the
     Task 4 Report (under docs/)
- rh: Relative Humidity setpoint (50, 60)
- v: ventilation system, as follows:
    + 0: none
    + 1: Exhaust Only
    + 2: CFIS
    + 3: HRV
    + 4: ERV
- sz: building size, one of sm, md, lg (last # in name)

The main function, *sim_line*, takes six parameters corresponding to
the bullet points above.  Multiple CSV files are produced, one per
system.

# postprocessing

This directory contains scripts to summarize and display the outputs
from TRNSYS.  TRNSYS, as configured by the TRD files, writes several
.dat files for each scenario.  Each file has one row per hour, and one
column per variable.  Columns are separated by tabs.  The variables
are spread over several files; each file has a row for every hour of
the year.

*process.py* is used to produce tables of annual values from the hourly
data.  It uses the same specification files as TRN_Resdh4.py, to
correctly name each row of the summary.  The fields used in the name
are also used to sort the output data.  process.py calls several
functions in *graphs.py*, which uses the python library *matplotlib* to
graph the hourly data.

process.py reads all of the hourly output for a given simulation run
and creates a python object, which is passed to each output function.
The member variables of this object are named after the column heads
in the TRNSYS .dat files, while the values are *numpy* arrays of length
8760 (one floating point value per hour).  The object is dynamically
defined, so any fields appearing in the .dat files will be available.
Modifying the *hourly_data* function, which reads the .dat files, is
not necessary.  New summary columns and summary files can be created
by adding *output_row* lines to the *summarize_csv* function, which
take input in the format described above.

*physics.py* contains psychrometric functions to convert between
various units of temperature and humidity.

*parametrics.py* contains functions to parse the TRNSYS output format,
and utility functions which are less general than those in physics.py,
but likely to be useful in other TRNSYS projects.  (The functions in
process.py are mostly less general still, with notable exceptions.)

*weather.py* reads a *TMY2* file and converts it into a numpy recarray
including many of the most useful fields.  It is not complete,
however.

Several subdirectories within *postprocessing* contain the (incomplete)
analysis of field data from an AAON heat pump with hot gas reheat,
installed in New Orleans.  *2011-graphs* contains graphs produced early
in the debugging of the RP-1449 project.

# lookups

Several parts of the model take additional parameters.  Because these
are reused in many scenarios, across multiple projects, they are
defined in separate lookup files. Examples, with some relevant
parameters, include:

- Air Conditioner (CFM/ton, W/CFM, EER)
- Dehumidifier (CFM, moisture removal rate, W/CFM)
- Infiltration (shelter class, wind coefficient)

These are exposed as pulldown menus in the graphical interface to
*TRN_Resdh4*, and are specified by row number in the CSV simulation
specifications.  *TRN_Resdh4.py* reads these lookups and writes the
values into the TRD.

# Manual J

For each zone, HERS level, and building size, a Manual J calculation
was performed using Elite RHVAC.  These are the input files for RHVAC.
The results are summarized in the Excel file excel/RP-1449
Calculations.xls.  gensim.py writes the calculated tonnage for each
scenario into the CSV simulation specifications.

# old-Hugh-types

This directory contains the Fortran code for TRNSYS components (types)
which Hugh Henderson provided.  During the RP-1449 project, only Hugh
compiled these components, and the code in this directory is probably
out of date --- not the code used for the final version of the report.
