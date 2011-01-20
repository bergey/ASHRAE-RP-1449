#!/usr/bin/python
import os
import shutil
from os import chdir, system, sys
from os.path import exists
from glob import glob
from subprocess import check_call, call
#from matplotlib import use
#import matplotlib.backends.backend_tkagg as backend
#from post_install import _get_key_val, _winreg
from csv import reader,writer,DictWriter, DictReader
from e_rate import e_rate
#use('Agg')
logf = 0

# path to external harddrive dir
external = '/cygdrive/d/'

def eia_e_rate(dt,kw,util_id,cat,state,Dir):

    #Class_txt = ['Residential','Commercial','Industrial','Other','Total']
    if cat.upper() == 'R': revI = 5
    elif cat.upper() =='C':revI = 8
    elif cat.upper() =='I':revI = 11
    elif cat.upper() =='O':revI = 14
    elif cat.upper() =='T':revI = 17

    f = open("..\util_rates\\f826util2004.csv",'r+')
    ReadOpt = reader(f)
    
    ckwh = [0]*12
    for row in ReadOpt:
        if row[0] == util_id and row[2] == state:
            ckwh[int(row[4])-1] = float(row[revI])/float(row[revI+1])
            util_name = row[1]
    f = open(Dir + "eia_rate.txt",'w+')
    f.write("EIA UTILITY RATE DATA "+'\n\n')
    f.write("Utility Name: "+str(util_name)+'\n')
    f.write("         ID: "+str(util_id)+'\n')
    f.write("      State: "+state+'\n')
    f.write("   Category: "+ cat+'\n')
    f.write("   Rate Year: 2004"+'\n') #Change utility rate year as per file
    f.write('\n')
    f.write('_'*24+'\n')
    f.write("Month  Rate         kWh"+'\n')
    f.write('-'*24+'\n')
    Months =['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    #Monthly Consumption
    for i,r in enumerate(ckwh):
        f.write(Months[i]+ '  |%3.3f | %10.2f' % (r,sum([kw[j] for j,t in enumerate(dt) if t.month == i+1]))+'\n')
    cst=[0]*12
    for i in range(12):
        cst[i] = ckwh[i] * sum([kw[j] for j,t in enumerate(dt) if t.month == i+1])
    f.write('_'*24+'\n')
    f.write('   Total kWh %11.2f\n'%sum(kw))
    f.write('    Total Cost %8.2f\n'%sum(cst))
    return cst


def process_outputs(path,run):
    from datetime import datetime, timedelta
    from dt_dict import dt_dict

    from numarray import asarray, where, reshape, compress

    s = system("dir " + path)
    if s != 0: system('mkdir ' + path)
    system("copy for_*.dat " + path)
    system("copy SimRuns.csv " + path)
    chdir(path)
    
    ##### Output Into data.out#####
    
    f = open('data.out', 'w')
    ff = glob('for_*.dat')
    
    fcase = open('SimRuns.csv', 'r')
    CaseLines = fcase.readlines()
    fcase.close()    
    CaseVars = CaseLines[run].replace('\n', '').split(',')
    CaseTags = CaseLines.pop(0).replace('\n', '').split(',')
    
    
    if len(ff) == 0:
        f.write('-1')
        f.close()
        return
    
    for each in ff:
        fz = open(each)
        tags = fz.readline()
        tags = tags.replace("\n", "")
        tags = [temp.strip() for temp in tags.split('\t')]
        t = fz.read()
        fz.close()
        t = t.replace("\n", '\t')
        while t[-1] == '\t': t = t[:-1]
        t = t.split('\t')
        for x in range(len(tags)):
            if tags[x] != '':
                exec(tags[x] + " = asarray([float(temp) for temp in t[x::len(tags)]])")

    dt = []
    
    for x in range(len(TIME)):
        dt.append(datetime(2005, 1, 1) + timedelta(hours=1) * x)
    dt = dt_dict(dt)
    
    
    e_rate_file = None
    eia_util_id = None
    eia_category = None
    eia_state = None
    util_rate = None
    GasRate = None
    GasCost = 0
    #print CaseTags
    #print CaseVars
    for z,Tags in enumerate(CaseTags):
        Tags = Tags.strip().upper()
        if CaseVars[z] == '-':
            continue
        if Tags == 'E_RATE_FILE':
            e_rate_file = CaseVars[z]
        if Tags == 'EIA_UTIL_ID':
            eia_util_id = CaseVars[z]
        if Tags == 'EIA_CATEGORY':
            eia_category = CaseVars[z]
        if Tags == 'EIA_STATE':
            eia_state = CaseVars[z]
        if Tags =='GASRATE':
            print CaseVars[z]
            GasRate = float(CaseVars[z])

    if not locals().has_key('Qh_gas'):
        Qh_gas = asarray([0.])
    NetKW = ((LIGHTS + EQP)/3600 +
             RTFc * ACKW +
             KWHT * RTFh * (1 - (Qh_gas.sum() > 0)) / 3412 +
             RTFacf * FANKW +
             RTFdf * DFANKW +
             RTFd * DKW +
             rtfvf * KWVF +
             rtfxf * KWXF +
             rtfhf * KWHF)

    if not (e_rate_file is None):
        rate = e_rate(rate='..\\util_rates\\' + e_rate_file, dt=dt, kw=NetKW, power_factor=0.9, verbose=1, verbose_file='utility.out')
        EnergyCost = [sum(c) for c in  rate['cost']]
    elif not (eia_util_id is None):
        if float(eia_util_id) < 1:
            EnergyCost = [float(eia_util_id) * kw for kw in NetKW]
        elif eia_category != None and eia_state != None:
            dtp = []
            eia_util_id = str(int(float(eia_util_id)))
            for x in range(len(TIME)):
                dtp.append(datetime(2005, 1, 1) + timedelta(hours=1) * x)
            rate = eia_e_rate(dtp, NetKW, eia_util_id, eia_category, eia_state, '')
            EnergyCost = rate
        else:
            rate = e_rate(rate='..\\util_rates\\CONED_SC2-1_NYC_PVYR', dt=dt, kw=NetKW, power_factor=0.9, verbose=1, verbose_file='utility.out')
            EnergyCost = [sum(c) for c in  rate['cost']]
    else:
        rate = e_rate(rate='..\\util_rates\\CONED_SC2-1_NYC_PVYR', dt=dt, kw=NetKW, power_factor=0.9, verbose=1, verbose_file='utility.out')
        EnergyCost = [sum(c) for c in  rate['cost']]
            

    if GasRate != None:     
        GasCost = float(GasRate) * ((RTFd * DGAS / 100) + (Qh_gas * RTFh / 100000))
    else:
        GasCost = 0.9 * ((RTFd * DGAS / 100) + (Qh_gas * RTFh / 100000))
    GasCost = asarray(GasCost)
    EnergyCost = asarray(EnergyCost)
    
    
    # Run Number (A/C type and DH type)
    f.write('%i%.2i,' % (ANO[0], DNO[0]))
    
    # Overall RH Data
    i = where(RHi > 60, 1, 0)
    f.write('%.2f,%i,%.2f,' % (RHi.mean(), i.sum(), RHi.max()))
    
    # Occupied RH Data
    f.write('%.2f,%i,%.2f,' % ((OCC * RHi).sum() / OCC.sum(), (OCC * i).sum(), (OCC * RHi).max()))
    
    # CO2
    try: f.write('%.2f,' % ((OCC * C_i).sum() * 1e6 / OCC.sum()))
    except: f.write('0,')
    f.write('%.2f,' % (C_i.max() * 1e6))
    
    # AC SHR and EER
    try: f.write('%.2f,' % ((Qsac).sum() / ((Qsac).sum() + (Qlac).sum())))
    except: f.write('0,')

    try: f.write('%.2f,' % (((Qsac + Qlac)).sum() / (ACKW * RTFc).sum() / 1e3))
    except: f.write('0,')
    
    # Various Runtimes
    vars = ['RTFc', 'RTFe', 'RTFh', 'RTFrh', 'RTFacf', 'RTFd', 'RTFdf', 'rtfvf',
            'rtfxf', 'rtfhf']
    for each in vars: 
        if locals().has_key(each) == False:
            exec each + ' = asarray([0.])'
    l = [
        RTFc.sum(),     # AC Runtime
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
    fmt_str = ','.join(['%.1f' for each in l]) + ','
    f.write(fmt_str % tuple(l))

    for i in range(len(vars)):
        print vars[i], '\t', l[i]
    
    # Power and Gas Use
    vars = ['ACKW', 'RTFc', 'KWHT', 'RTFh', 'Qh_gas', 'Qrh', 'RTFrh', 'RTFacf',
            'FANKW', 'RTFd', 'DGAS', 'DKW', 'DFANKW', 'rtfvf', 'KWVF', 'rtfxf',
            'KWXF', 'KWHF', 'LIGHTS', 'EQP', 'NetKW', 'EnergyCost', 'GasCost']
    for each in vars: 
        if locals().has_key(each) == False:
            exec each + ' = asarray([0.])'
    l = [
        (ACKW * RTFc).sum(),                 # AC Electric Use (kWh)
        (KWHT * RTFh).sum() *
           (1 - (Qh_gas.sum() > 0)) / 3412,  # Heater Electric Use (kWh)
        (Qh_gas * RTFh).sum() / 100000,      # Heater Gas Input (Therms)
        (Qrh * RTFrh).sum() / 1000,          # Reheat (MBTU)
        (RTFacf * FANKW).sum(),              # Supply Fan Electric Use (kWh)
        (RTFd * DGAS).sum() / 100.,          # Des Unit Gas Use (therms)
        (RTFd * DKW).sum(),                  # Des Unit Electric Use (kWh)
        (RTFdf * DFANKW).sum(),              # Des FAN Electric Use (kWh)
        (rtfvf * KWVF).sum(),                # Vent Damp/Fan Electric Use (kWh)
        (rtfxf * KWXF).sum(),                # Exhaust Fan Electric Use (kWh)
        (rtfhf * KWHF).sum(),                # HRV Electric Use (kWh)

        (LIGHTS + EQP).sum() / 3600,         # Lights & Equipment (kWh)
        NetKW.sum(),                         # Total Electric Use (kWh)
        EnergyCost.sum(),                    # Total Electricity Cost ($)
        GasCost.sum(),                       # Total Gas Cost ($)
        ]
    fmt_str = ','.join(['%.1f' for each in l]) + '\n'
    f.write(fmt_str % tuple(l))
    
    # Monthly Table
    for x in range(1, 13):
        j = where(dt["month"] == x, 1, 0)
        
        # Cooling Loads
        f.write('%.0f,%.0f,%.0f,' % ((Qsac*RTFc*j).sum()/1e3, (Qlac*RTFc*j).sum()/1e3,
            (Qsac*RTFc*j+Qlac*RTFc*j).sum()/1e3))
        
        # RH Above 60
        f.write('%i,%i,' % ((i*j).sum(),(OCC*i*j).sum()))
        
        # Various Runtimes
        f.write('%.0f,%.0f,%.0f,%.0f,' % ((RTFc*j).sum(), (RTFacf*j).sum(), (RTFd*j).sum(), (RTFdf*j).sum()))
        
        # Power and Gas Use 
        f.write('%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n' % ((ACKW*RTFc*j).sum(),(Qh*RTFh*j).sum()*(1-(Qh_gas.sum()>0))/3412,(Qh_gas*RTFh*j).sum()/100000,(Qrh*RTFrh*j).sum()/1000,(RTFacf*FANKW*j).sum(),
                (RTFd*DGAS*j).sum()/100.,(RTFd*DKW*j).sum(), (RTFdf*DFANKW*j).sum(),((LIGHTS+EQP)*j).sum()/3600,(NetKW*j).sum(),EnergyCost[x-1],(GasCost*j).sum()))
            
    
#    for x in range(1, 366):
#        j = where(dt["dayofyear"] == x, 1, 0)
#       
#        # Indoor-Outdoor Humidity Data
#        f.write('%.2f,%.2f,' % ((Wi*j).sum()/j.sum()*7000., (Wo*j).sum()/j.sum()*7000.))
#        try: f.write('%.2f,%.2f,' % ((Wi*j*OCC).sum()/(j*OCC).sum()*7000., (Wo*j*OCC).sum()/(j*OCC).sum()*7000.))
#        except: f.write('0,0,')
#       
#        # TAO, Cooling and Heating Load
#        f.write('%.2f,%.2f,%.2f\n' % ((To*j).sum()/j.sum(), ((Qsac+Qlac)*j*RTFc).sum()/1e6, (RTFh*Qh*j).sum()/1e6))
        
    f.close()
    
    ###### Output into daily_data.out ########
    f = open('daily_data.out', 'w')
    f.write(str(dt["dt"][8758]))
    for z in range(8760):
        # Date
        f.write("%s,%s," % (dt["dt"][z].strftime("%#m/%#d/%Y"), dt["dt"][z].strftime("%H:%M:%S")))
        
        # Indoor-Outdoor T, W and RH
        f.write('%.1f,%.1f,%.1f,%.1f,%.1f,' % (To[z], 
            Wo[z]*7000., Ti[z], Wi[z]*7000., RHi[z]))
        
        # System Runtimes
        f.write('%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,' % (RTFacf[z], 
            RTFdf[z], RTFe[z], RTFc[z], RTFd[z], RTFh[z], RTFrh[z]))
        
        # CO2
        f.write('%.1f\n' % (C_i[z]*1e6))
    
    f.close()
    
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

    s = "Completed Successfully\n"
    sys.stdout.write(s)
    sys.stderr.write(s)
    return

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
    print DestFolder
    fcase = open("%s/SimRuns.csv" % DestFolder)
    #print fcase
    print "Opened SimRuns.csv"
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
    sys.stderr = logf

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
                trd = 'CaseRun%s.trd' % i
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
