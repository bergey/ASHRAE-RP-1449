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

