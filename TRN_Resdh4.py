#!/usr/bin/python
import os
import shutil
from os import chdir, system, sys
from os.path import exists
from glob import glob
from subprocess import check_call, call
import datetime as dt
#from matplotlib import use
#import matplotlib.backends.backend_tkagg as backend
#from post_install import _get_key_val, _winreg
from csv import reader,writer,DictWriter, DictReader
#use('Agg')
logf = 0

# path to external harddrive dir
external = '/cygdrive/d/'

    
##    ##### Plots Section #####
##    # Indoor-Outdoor Humidity Plot
##    close()
##    figure(1)
##    ax = subplot(111)
##    res_Wo = reshape(Wo, 365, 24)*7000.
##    res_Wi = reshape(Wi, 365, 24)*7000.
##    i = where(OCC == 1, 1, 0)
##    i = reshape(i, 365, 24)
##    
##    d_Wo = []
##    d_Wi = []
##    for x in range(len(res_Wo)):
##        try:
##            d_Wo.append((compress(i[x], res_Wo[x])).mean())
##            d_Wi.append((compress(i[x], res_Wi[x])).mean())
##        except:
##            d_Wo.append(-99.)
##            d_Wi.append(-99.)
##        
##    d_Wo = asarray(d_Wo)
##    d_Wi = asarray(d_Wi)
##    
##    i = where(d_Wo != -99, 1, 0) * where(d_Wi != -99, 1, 0)
##    plot(compress(i, d_Wo), compress(i, d_Wi), "rx")
##    
##    d_Wo = asarray([each.mean() for each in res_Wo])
##    d_Wi = asarray([each.mean() for each in res_Wi])
##    plot(d_Wo, d_Wi, "g+")
##    
##    title("Indoor-Outdoor Humidity Comparison")
##    ax.set_ylim([0,150])
##    ax.set_xlim([0,150])
##    ax.set_yticks(asarray(range(6))*30)
##    ax.set_xticks(asarray(range(6))*30)
##    ylabel("Daily Indoor Humidity (gr/lb)")
##    xlabel("Daily Outdoor Humidity (gr/lb)")
##    legend(["Occupied", "All Hours"], 'best')
##    
##    plot([0,150],[0,150], 'k')
##    a = savefig('Humidity Trend Plot.png')
##    close()
##    
##    # Load Lines
##    figure(1)
##    d_Qcool = asarray([each.sum() for each in reshape((Qsac+Qlac)*RTFc, 365, 24)/1.e6])
##    d_Qheat = asarray([each.sum() for each in reshape(Qh*RTFh, 365, 24)/1.e6])
##    d_tao = asarray([each.mean() for each in reshape(To, 365, 24)])
##    
##    i = where(d_Qcool > 0, 1, 0)
##    j = where(d_Qheat > 0, 1, 0)
##    labels = []
##    if i.sum():
##        plot(compress(i, d_tao), compress(i, d_Qcool), "bx")
##        labels.append("Daily Cooling Load")
##    if j.sum():
##        plot(compress(j, d_tao), compress(j, d_Qheat), "ro")
##        labels.append("Daily Heating Load")
##    if i.sum() or j.sum(): legend(labels, 'upper center')
##    title("Daily Cooling and Heating Loads")
##    ylabel("Daily Load (MMBtu/day)")
##    xlabel("Daily Outdoor Temperature (F)")
##    a = savefig('Daily Load Lines.png')
##    close()
##    
##    # Ambient Humidity Histogram
##    hist_plot(Wo*7000., 5, var_range = [0, 150], color = 'r', filename = "Ambient Humidity Histogram.png",
##        y_label = "Number of Hours", x_label = "Ambient Humidity", units = "gr/lb",
##        h_title = "Ambient Humidity Histogram", dpi=100)
##    
##    # Space Relative Humidity Histogram
##    hist_plot(RHi, 1, var2 = compress(OCC, RHi), color = 'g', color2 = 'r',
##        y_label = "Number of Hours", x_label = "Space Relative Humidity", units = "%", 
##        h_title = "Space Relative Humidity Histogram", dpi=100)
##        
##    ax = subplot(111)
##    x_range = ax.get_xlim()
##    y_range = ax.get_ylim()
##    plot([(x_range[1]-x_range[0])*.95+x_range[0]], [(y_range[1]-y_range[0])*.95+y_range[0]], 'gs')
##    plot([(x_range[1]-x_range[0])*.95+x_range[0]], [(y_range[1]-y_range[0])*.95+y_range[0]], 'rs')
##    legend(["Unoccupied", "Occupied"])
##    
##    a = savefig(filename = "Space Relative Humidity Histogram.png")
##    close()
##    
##    # Space Temperature Histogram
##    hist_plot(Ti, 0.2, var2 = compress(OCC, Ti), color = 'b', color2 = 'y',
##        y_label = "Number of Hours", x_label = "Space Temperature", units = "F",
##        h_title = "Space Temperature Histogram", dpi=100)
##        
##        
##    ax = subplot(111)
##    x_range = ax.get_xlim()
##    y_range = ax.get_ylim()
##    plot([(x_range[1]-x_range[0])*.95+x_range[0]], [(y_range[1]-y_range[0])*.95+y_range[0]], 'bs')
##    plot([(x_range[1]-x_range[0])*.95+x_range[0]], [(y_range[1]-y_range[0])*.95+y_range[0]], 'ys')
##    legend(["Unoccupied", "Occupied"])
##    
##    a = savefig(filename = "Space Temperature Histogram.png")
##    close()
##    
##    # Cooling Runtime Histogram
##    i = where(RTFc > 0, 1, 0)
##    if i.sum():
##        hist_plot(compress(i, RTFc), .025, var_range = [0, 1], filename = "Cooling Runtime Histogram.png", 
##            color = 'b', y_label = "Number of Hours", x_label = "Cooling Runtime Fraction",  
##            units = "-", h_title = "Cooling Runtime Histogram", dpi=100)

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
    #print "MnuOption is %s" % row
    return row


def MakeCaseFile(Run, TRDFile, DestFolder, DestTRD):
    #print DestFolder
    fcase = open("%s/SimRuns.csv" % DestFolder)
    #print fcase
    #print "Opened SimRuns.csv"
    CaseLines = fcase.readlines()
    fcase.close()
    #print "Closed SimRuns.csv"

    #print Run
    #print len(CaseLines)

    CaseTags = CaseLines.pop(0).replace('\n', '').split(',') # remove 0 line
    try:
        RunColumn = CaseTags.index('Run')
        #print "Run is in column %s" % RunColumn
        for line in CaseLines:
            line = line.replace('\n','').split(',')
            #print "line is %s long" % len(line)
            id = int(float(line[RunColumn]))
            #print "scanning Run Number %s" % id
            if id == Run: # breaks if Run is not a number
                CaseVars = line
                break
    except:
        print "Couldn't use Run Column; Assuming in order from 1"
        CaseVars = CaseLines[Run-1] # removed 0 line, above
    
    #fcurrCase = open('casefile','w')
    #fcurrCase.write(CaseLines[0])
    #fcurrCase.write(CaseLines[Run-1])

    #fcurrCase.close()
    #print "closed casefile"
    f1 = open(TRDFile, 'r')
    TRDLines = f1.readlines()
    f1.close()
    #print "read %s" % TRDFile;
    #print CaseTags
    
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
            CaseVars.extend([opt[2],opt[3],opt[4],opt[5],opt[6],opt[7],opt[8],opt[9],opt[10],opt[11],opt[12],opt[13],opt[14],opt[15],opt[16],opt[17],opt[18]])
        elif case.upper() == 'ANO':
            opt = GetMnuOption(0,str(int(float(CaseVars[i]))),'AC_Units.txt')
            if opt == None: continue
            CaseTags.extend(['IAC','AC_EER','AC_SHR','WCFM_AC','chrg_ratio','exp_type','rown','hparea','ihp'])
            CaseVars.extend([opt[2],opt[3],opt[4],opt[6],opt[7],opt[8],opt[9],opt[10],opt[11]])
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
    var_changed = [0]*len(CaseTags)
    #print "extended CaseTags"
    
    for z in range(1, len(CaseTags)):
        Tag = CaseTags[z]
        Var = CaseVars[z]
        # Replacement Conditioning Section
        if Var == "-":
            var_changed[z] = 1      
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
            #print "rewrote weather location"

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
                    #print "rewrote building assignment"
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
                var_changed[z] = 1

            elif Tag.upper() == 'WEATHERFILE':
#               if LineArray[0].upper() == 'ASSIGN' and LineArray[2] == '20' and warray != False:               
                if 'ASSIGN' in LineArray and '20' in LineArray and warray != False:
                    TempLine = TempLine.replace(LineArray[1], Var.upper() + '.tm2')
                    do_break = True
                    #print LineArray, TempLine, Var
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
                var_changed[z] = 1
                do_break = True

            else:
                continue
            
            if TempLine != TRDLine:
                TRDLines[TRDLines.index(TRDLine)] = TempLine
                var_changed[z] = 1
                if do_break: break
    
    #print "opening %s" % DestTRD
    fout = open(DestTRD, 'wb')
    fout.writelines(TRDLines)
    fout.close()
    if logf: logf.write(str([t for t,v in zip(CaseTags,var_changed) if v == 0]))
    return

if __name__ == "__main__":
    from time import sleep
    if len(sys.argv) > 2: path = sys.argv[2]
    logf = open('log.txt','a')
    #sys.stderr = logf

    if sys.argv[1] == '-load':
        s = system("del Current\\*.* /q")
        if s == 1: system("mkdir Current")
        logf = open('log.txt','a')    
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
        TRNSYSPath = '.'
        cmd = '%s "%s"  %s' % (os.path.join(os.getcwd(), "TRNExe.exe"), sys.argv[2], "/n")
        print cmd
        system(cmd)
        #system('%s\%s "%s" %s' % (os.getcwd(), "TRNExe.exe", sys.argv[2], "/n"))

    elif sys.argv[1] == '-edit':
        TRNSYSPath = '.'
        system('""%s\%s" "%s"' % (TRNSYSPath, "Exe\TRNEdit.exe", sys.argv[2]))
    elif sys.argv[1] == '-trd_write':
        logf.write('\n\n'+ str(sys.argv)+'\n')
        print sys.argv
        Run = int(sys.argv[2])
        DestFolder = sys.argv[3]
        TRDFile = sys.argv[4]
        DestTRD = sys.argv[5]
        print DestTRD
        MakeCaseFile(Run, TRDFile, DestFolder, DestTRD)
    elif sys.argv[1] == '-batch':
# read input from 1+ CSVs, run a simulation for each row, save results
        # setup filepaths
        executable = os.path.join(os.getcwd(), 'TRNExe.exe')

        # per argument
        for csvname in sys.argv[2:]:
            print "beginning file: %s" % csvname
            if 'log' in dir():
                log.close()
            try:
              if os.path.exists('batch-log'):
                  os.rename('batch-log', 'batch-log.0')
              log = open('batch-log', 'w')
            except:
                print "failed to open log"
            # store the results of each csv in a separate directory
            dirname = csvname.replace(' ','-').replace('.csv','')
            dirname = os.path.join(external, dirname)
    
            # initialize 
            if exists(dirname):
                print "%s exists" % dirname
            else:
                os.mkdir(dirname)
                print "created %s" % dirname
            parametrics = reader(open(csvname))
            print "opened %s" % csvname
            simruns = writer(open(os.path.join(dirname,'SimRuns.csv'),'w'))
            print "opened simruns"
            for line in parametrics:
                simruns.writerow(line[2:])
            del simruns # this is important, before we open the file again
            print "finished writing simruns"

            parametrics = DictReader(open(csvname))
            # loop over sims in this file
            for line in parametrics:
                print line
                i = int(float(line['Run']))
                print "Run: %s" % i
                run_dir = os.path.join(dirname, 'Run%s' % i)
                if exists(run_dir):
                    print "%s exists" % run_dir
                else:
                    os.mkdir(run_dir)
                    print "created %s" % run_dir
                # Create the TRD
                trd = '{0}.trd'.format(line['Desc'].replace(' ','-'))
                MakeCaseFile(i, line['BaseFile'], dirname, trd)
                # Try to change the file output location
                # Run the simulation
                cmd = [executable, trd, '/n']
                print cmd
                call(cmd, stdout=log, stderr=log)
                # move output TODO this prevents parallelism
                for file in glob('for*'):
                    shutil.move(file, os.path.join(run_dir,file))
                shutil.move(trd, os.path.join(run_dir, trd))
    elif sys.argv[1]=='-dryrun':
      dirname = dt.datetime.now().strftime('%Y-%m-%d-%H%M-trds')
      if not exists(dirname):
        os.mkdir(dirname)
      for csvname in sys.argv[2:]:
        parametrics = reader(open(csvname))
        print("opened {0}".format(csvname))
        simruns = writer(open(os.path.join(dirname, 'SimRuns.csv'),'w'))
        for line in parametrics:
            simruns.writerow(line[2:])
        del simruns # this is important, before we open the file again
        parametrics = DictReader(open(csvname))
        for line in parametrics:
            trd = '{0}.trd'.format(line['Desc'].replace(' ','-'))
            print("creating {0}".format(trd))
            i = int(float(line['Run']))
            MakeCaseFile(i, line['BaseFile'], dirname, trd)
            shutil.move(trd, os.path.join(dirname, trd))
    else:
          #raise
#except:
          print """
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
        -batch  Run simulations as specified in a csv file, one per row
      """
