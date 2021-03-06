#!/usr/bin/python
import os
import shutil
from os import chdir, system, sys
from os.path import exists
from glob import glob
from subprocess import check_call, call
import datetime as dt
import sys
import json
from csv import reader,writer,DictWriter, DictReader

# path to store output .dat files
output_dir = json.loads(open('trnbatch.conf').read())['output_dir']

def crlf_print(item, file=sys.stdout):
    """Make lineending CRLF regardless of platform"""
    if os.linesep == '\r\n':
        file.write(item)
    else:
        file.write(item.replace('\n', '\r\n'))

def GetMnuOption(col, Opt, OptFile):
    from csv import reader, writer, DictWriter
    f = open(OptFile, "r+")
    ReadOpt = reader(f)
    for row in ReadOpt:
        if len(row) > 1:
            if str(row[col]).strip().upper() == Opt.strip().upper():
                break
            else:
                row = None                     
    #print("MnuOption is %s" % row)
    return row

def CaseFileFromCSV(Run, TRDFile, DestFolder, DestTRD):
# OBS by DictReader
    #print(DestFolder)
    fcase = open("%s/SimRuns.csv" % DestFolder)
    #print(fcase)
    #print("Opened SimRuns.csv")
    CaseLines = fcase.readlines()
    fcase.close()
    #print("Closed SimRuns.csv")

    #print(Run)
    #print(len(CaseLines))

# OBS by DictReader
    CaseTags = CaseLines.pop(0).replace('\r', '').replace('\n', '').split(',') # remove 0 line
    try:
        RunColumn = CaseTags.index('Run')
        #print("Run is in column %s" % RunColumn)
        for line in CaseLines:
            if line == '\n':
                print("dropped blank line")
                continue # native windows takes \r as newline
                         # reads \n as a second, blank line
            line = line.replace('\r', '').replace('\n','').split(',')
            #print("line is %s long" % len(line))
            id = int(float(line[RunColumn]))
            #print("scanning Run Number %s" % id)
            if id == Run: # breaks if Run is not a number
                CaseVars = line
                break
    except:
        print("Couldn't use Run Column; Assuming in order from 1")
        CaseVars = CaseLines[Run-1] # removed 0 line, above
    
    #fcurrCase = open('casefile','w')
    #fcurrCase.write(CaseLines[0])
    #fcurrCase.write(CaseLines[Run-1])

    #fcurrCase.close()
    #print("closed casefile")
    f1 = open(TRDFile, 'r')
    TRDLines = [line.replace('\r', '') for line in f1.readlines()]
    f1.close()
    #print("read %s" % TRDFile;)
    #print(CaseTags)
    spec = dict(zip(CaseTags, CaseVars))
    MakeCaseFile(spec, DestTRD)
    

def MakeCaseFile(spec, DestTRD):
    CaseTags = spec.keys()
    CaseVars = spec.values()
    for i,case in enumerate(CaseTags[:]):
        if CaseVars[i] == "-":
            continue
        elif case.upper() == 'RES_DNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'res_dh_units.txt')
            if opt == None: continue
            CaseTags.extend(['DTYPE','DPAR3a','DPAR4','DPAR5','DPAR6','DPAR7','DPAR8','DPAR9','DPAR10','DPAR11','DPAR12','DPAR13','DPAR14','DPAR15','DPAR16','DPAR17','DPAR18'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[5],opt[6],opt[7],opt[8],opt[9],opt[10],opt[11],opt[12],opt[13],opt[14],opt[15],opt[16],opt[17],opt[18]])
        elif case.upper() == 'COM_DNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'Com_Des_units.txt')
            if opt == None: continue
            CaseTags.extend(['DTYPE','DPAR3a','DPAR4','DPAR5','DPAR6','DPAR7','DPAR8','DPAR9','DPAR10','DPAR11','DPAR12','DPAR13','DPAR14','DPAR15','DPAR16','DPAR17','DPAR18'])
            CaseVars.extend(opt[2:])
        elif case.upper() == 'ANO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'ac_units.txt')
            if opt == None: continue
            CaseTags.extend(['IAC','AC_EER','AC_SHR','WCFM_AC','chrg_ratio','exp_type','rown','hparea','ihp','AC_EER_lo', 'AC_SHR_lo', 'tons_frac_lo', 'wcfm_ac_lo', 'cfm_frac_lo'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[6],opt[7],opt[8],opt[9],opt[10],opt[11], opt[12], opt[13], opt[14], opt[15], opt[16]])
        elif case.upper() == 'LNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'LatDeg.txt')
            if opt == None: continue
            CaseTags.extend(['TWET','GAMMA','NTUo_nom','fspd_off2','ISHRF'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[5],opt[8]])
        elif case.upper() == 'SINZONE_BNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'Single_Zone_Buildings.txt')
            if opt == None: continue            
            CaseTags.extend(['btype','ZAR','NO_ZONE','Xdep','ACH_file','WALLH','Peop','peop_Q','Lt_WPerFt','Eq_WPerFt','BUIFILE'])
            CaseVars.extend([opt[2], opt[4],   opt[5],opt[6],  opt[7], opt[8],opt[9], opt[10], opt[11], opt[12],   opt[3].split('.')[0]])
        elif case.upper() == 'TWOZONE_BNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'Two_Zone_Buildings.txt')
            if opt == None: continue
            CaseTags.extend(['btype','ZAR','NO_ZONE','Xdep','ACH_file','WALLH','Peop','peop_Q','Lt_WPerFt','Eq_WPerFt','BUIFILE'])
            CaseVars.extend([opt[2], opt[4],   opt[5],opt[6],   opt[7], opt[8],opt[9], opt[10], opt[11],    opt[12],    opt[3].split('.')[0]])
        elif case.upper() == 'ACH_TYPE':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'Infiltration.txt')
            if opt == None: continue
            CaseTags.extend(['K1','K2','K3','A','B','C'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[5],opt[6],opt[7]])
        elif case.upper() == 'TNO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'tstat.txt')
            if opt == None: continue
            CaseTags.extend(['TDBND','Ta_o','Taua','taue','HDBND','CDBND'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[5],opt[6],opt[7]])        
    #print("extended CaseTags")
    
    for Tag, Var in zip(CaseTags, CaseVars):
        # Replacement Conditioning Section
        if Var == "-":
            continue
            
        
        if Tag.upper() == 'WEATHERFILE':
            f = open('tmy_cities.txt')
            t = f.readlines()
            t.pop(0)
            warray = False
            for wline in t:
                if Var.upper() in wline.upper():
                    warray = wline.replace('\n', '').split(',')
                    break
            f.close()
            #print("rewrote weather location")

        if Tag.upper() == 'TESSMODEL':
            tess_path = '../../rice_dh/'
            tess_file = tess_path + 'tess_building_map.dat'

            nc = len(open(tess_file).readline().split(','))
            t = open(tess_file).read().replace('\r', '').replace('\n', ',')
            t = t.split(',')
            for x in range(nc): t.pop(0)
            
            t_upper = [each.upper() for each in t]
            id = t_upper.index(Var.upper())
            buifile = t[id+1].strip()
            schfiles = [each.strip() for each in t[id+2:id+nc-1]]
            trdpt_file = t[id+nc-1].strip()

            t = open(tess_path + trdpt_file.strip()).readlines()    

            # Block 1           
            sid_part_file = t.index('''*                           TESS Block 1\n''')
            sid_trd_file = TRDLines.index('''*                           TESS Block 1\n''')
            eid_part_file = t.index('''*                           TESS Block 1  ----END-----\n''')
            eid_trd_file = TRDLines.index('''*                           TESS Block 1  ----END-----\n''')
            TRDLines[sid_trd_file:eid_trd_file] = t[sid_part_file:eid_part_file]

            # Block 2
            sid_part_file = t.index('''*                           TESS Block 2\n''')
            sid_trd_file = TRDLines.index('''*                           TESS Block 2\n''')
            eid_part_file = t.index('''*                           TESS Block 2 - END\n''')
            eid_trd_file = TRDLines.index('''*                           TESS Block 2 - END\n''')
            TRDLines[sid_trd_file:eid_trd_file] = t[sid_part_file:eid_part_file]

            # Change Schedules
            schedules = ['BMFridge.sld', 'BMGarLgt.sld', 'BMLALgt.sld', 'BMMiscPlug.sld', 'BMOccSched.sld',
                         'BMPlugLgt.sld', 'BMProcess.sld', 'BMVTemp.slm', 'BMVent.slm', 'BMWndShade.slm']

            for x,sch in enumerate(schedules):
                for y,line in enumerate(TRDLines):
                    if sch in line:
                        id = line.index(sch)
                        TRDLines[y] = line.replace( line[id-3:id+len(sch)], schfiles[x] )
                        break

            # Change Building Model
            for x,line in enumerate(TRDLines):
                if '.bui' in line and 'ASSIGN' in line:
                    line_array = line.split('\\')
                    if len(line_array) == 1:
                        id = line.index('"')
                        TRDLines[x] = 'ASSIGN "' + buifile + line[id:]
                    else:
                        id = line_array[-1].index('"')
                        line_array[-1] = buifile + line_array[-1][id:]
                        TRDLines[x] = '\\'.join(line_array)
                    #print("rewrote building assignment")
                    break
            

        do_break = False
        for TRDLine in TRDLines:
            TempLine = TRDLine
            LineArray = TempLine.split()
            
            if len(LineArray) == 0: continue
            elif LineArray[0][0] == '*': continue

            elif Tag.upper() == 'BUIFILE' and LineArray[0].upper() == 'ASSIGN' and LineArray[2] == '32':
                TempLine = TempLine.replace(LineArray[1], Var + '.bui')
                do_break = True

            elif Tag.upper() == 'WEATHERFILE':
#               if LineArray[0].upper() == 'ASSIGN' and LineArray[2] == '20' and warray != False:               
                if 'ASSIGN' in LineArray and '20' in LineArray and warray != False:
                    TempLine = TempLine.replace(LineArray[1], Var.upper() + '.tm2')
                    do_break = True
                    #print(LineArray, TempLine, Var)
                elif "CITYNO" == LineArray[0].upper() and warray != False:
                    TempLine = TempLine.replace(LineArray[2], warray[0])
                elif "LAT" == LineArray[0].upper() and warray != False:
                    TempLine = TempLine.replace(LineArray[2], warray[2])
                elif "TGA" == LineArray[0].upper() and warray != False:
                    TempLine = TempLine.replace(LineArray[2], warray[4])
                elif "TGS" == LineArray[0].upper() and warray != False:
                    TempLine = TempLine.replace(LineArray[2], warray[5])
                elif "DMIN" == LineArray[0].upper() and warray != False:
                    TempLine = TempLine.replace(LineArray[2], warray[6].strip())
                    
            elif Tag.upper() == LineArray[0].upper() and LineArray[1] == '=':
                ##TempLine = TempLine.replace(LineArray[2], Var) ## This caused an error for "DPAR2a = 2" as the 2 in the DPAR2a is also replaced ##
                TempLine = LineArray[0] + ' = '+ Var + '\n'
                do_break = True

            else:
                continue
            
            if TempLine != TRDLine:
                TRDLines[TRDLines.index(TRDLine)] = TempLine
                if do_break: break
    
    #print("opening %s" % DestTRD)
    fout = open(DestTRD, 'w')
    for line in TRDLines:
        crlf_print(line, file=fout)
    fout.close()
    return

def make_simruns(csvname, dirname):
    parametrics = reader(open(csvname))
    simruns = writer(open(os.path.join(dirname,'SimRuns.csv'),'w'))
    for line in parametrics:
        simruns.writerow(line[2:])
    del simruns # this is important, before we open the file again

def move_output(trd, dest):
    for file in glob('for_*'):
        shutil.move(file, os.path.join(dest,file))
    shutil.move(trd, os.path.join(dest, trd))

def run_trd(trd, dest):
    executable = os.path.join(os.getcwd(), 'TRNExe.exe')
    # Run the simulation
    cmd = [executable, trd, '/n']
    call(cmd, stdout=log, stderr=log)
    # after simulation
    run_dir = os.path.join(dest, trd[:-4])
    if not exists(run_dir):
        os.mkdir(run_dir)
    move_output(trd, run_dir)

def renew_log():
    global log
    if 'log' in dir():
        log.close()
    if os.path.exists('batch-log'):
        shutil.move('batch-log', 'batch-log.0')
    log = open('batch-log', 'w')

def usage():
    print("""
      Operates on TRNSYS results to generate data summaries and figures

      TRN_Resdh2 -option
      Options:
        -load run	If run is 0, data summaries and figure are generated.
          Otherwise data summaries and figures are reloaded into the
          "Current" directory from the corresponding "Archived_Run"
          directory.
        -archive run	Archives data summaries and figures in the "Current" directory
          into the appropriate "Archived_Run" directory.
        -copy file	Copies file into "Current" Directory.
        -listdir str 	Outputs results for search criteria into the file "dir.out".
          "str" is a search string and can contain wildcard entries.
        -rmdir run	Removes "Archived_Run" directory for the desired run.
        -runsim file  Launches TRNExe and executes specified file for simulation.
        -edit file	Launches TRNEdit and loads specified file.
        -case		Conditions Parametric Case File
        -batch  Run simulations as specified in a csv file(s), one per row
        -dryrun  Generate TRD files from specified csv file(s), do not run simulations
      """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit() # plain exit() isn't portable
    from time import sleep
    if len(sys.argv) > 2: path = sys.argv[2]

    if sys.argv[1] == '-load':
        s = system("del Current\\*.* /q")
        if s == 1: system("mkdir Current")
        if sys.argv[2] == '0':
            process_outputs("Current\\",int(sys.argv[3]))
            system("del *.dat")
        else:
            system('copy %s\\* Current\\' % path)
                    
    elif sys.argv[1] == '-archive':
        s = system('del "%s\\*.*" /q' % path)
        if s == 1: system('mkdir %s' % path)
        system('copy Current\\* %s' % path)    
    
    elif sys.argv[1] == '-copy':
        s = system('copy "%s" Current' % path)
        if s == 1:
            f = open('dir.out', 'w')
            f.write('-1')
            f.close()
        
    elif sys.argv[1] == '-listdir':
        s = system('dir "%s" /b /o-d > dir.out' % sys.argv[2])
        if s == 1:
            f = open('dir.out', 'w')
            f.write('-1')
            f.close()

    elif sys.argv[1] == '-rmdir':
        system('del "%s\\*.*" /q' % path)
        system('rmdir /s /q %s' % path)
        sleep(2)

    elif sys.argv[1] == '-move':
        system('move "%s" "%s"' % (sys.argv[2], sys.argv[3]))

    elif sys.argv[1] == '-runsim':
        for trd in sys.argv[2:]:
            renew_log()
            run_trd(trd, output_dir)

    elif sys.argv[1] == '-edit':
        TRNSYSPath = '.'
        system('""%s\%s" "%s"' % (TRNSYSPath, "Exe\TRNEdit.exe", sys.argv[2]))
    elif sys.argv[1] == '-trd_write':
        print(sys.argv)
        Run = int(sys.argv[2])
        DestFolder = sys.argv[3]
        TRDFile = sys.argv[4]
        DestTRD = sys.argv[5]
        print(DestTRD)
        CaseFileFromCSV(Run, TRDFile, DestFolder, DestTRD)
    
    elif sys.argv[1] == '-batch':
    # read input from 1+ CSVs, run a simulation for each row, save results

        # per argument
        for csvname in sys.argv[2:]:
            print("beginning file: %s" % csvname)
            renew_log()

            # store the results of each csv in a separate directory
            dirname = os.path.join( output_dir, csvname.replace(' ','-').replace('.csv','') )
    
            # initialize 
            if not exists(dirname):
                os.mkdir(dirname)
            # TODO remove whole simruns shenanigans, once CaseFileFromCSV doesn't need it
            make_simruns(csvname, dirname) # csv file used by CaseFileFromCSV

            parametrics = DictReader(open(csvname))
            # loop over sims in this file
            for line in parametrics:
                desc = line['Desc'].replace(' ', '-')
                print("Starting run {0}".format(desc))
                # Create the TRD
                trd = '{0}.trd'.format(desc)
                i = int(float(line['Run']))
                CaseFileFromCSV(i, line['BaseFile'], dirname, trd)
                run_trd(trd, dirname)

    elif sys.argv[1]=='-dryrun':
      dirname = dt.datetime.now().strftime('%Y-%m-%d-%H%M-trds')
      if not exists(dirname):
        os.mkdir(dirname)
      for csvname in sys.argv[2:]:
        parametrics = reader(open(csvname))
        print("opened {0}".format(csvname))
        make_simruns(csvname, dirname)
        parametrics = DictReader(open(csvname))
        for line in parametrics:
            trd = '{0}.trd'.format(line['Desc'].replace(' ','-'))
            print("creating {0}".format(trd))
            i = int(float(line['Run']))
            CaseFileFromCSV(i, line['BaseFile'], dirname, trd)
            shutil.move(trd, os.path.join(dirname, trd))
    else:
        usage()
