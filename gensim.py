import csv

head = ['Desc','','BaseFile','Run','SinZone_bno','WeatherFile','ACTON','ACCFM','ANO','WCFM_C','WCFM_H','THhi','THlo','TChi','TClo','fctyp5','ftim_ON5','ftim_OFF5','fctyp6','ilck61','fctyp7','ftim_ON7','ftim_OFF7','ilck71','fctyp8','ilck81','fctyp9','ilck91','VCFM','exh_cfm','Res_DNO','DSET','DCFM','DSIM_OPT', 'HRV_CFM', 'HRV_eL']

#MJ = {'z': 0, 'h': 0.5, 'o':1}
#Fan = {'E':0.3, 'P':0.5}
#Setpoint_cool = {'w':77, 'n':75}
#Setpoint_heat = {'w':70, 'n':72}

# Climate dependant parametrs
cfile = csv.reader(open('climate-dependant.csv'))
climate = []
cfile.next()
for line in cfile:
  climate.append(line)

vent0 = 58 # cfm, 62.2 rate, 2016 sf, 4 bedrooms

def order_line(d):
  return [d['Desc'],None]+[d[h] for h in head[2:]]

def sim_lines(m,s,f,t,climate):
  BaseFile = 'BSC-008.trd'
  if f=='E':  # ECM Motor in Air Handler
    ANO = 16
    WCFM_C = 0.3 # W/cfm
    WCFM_H = 0.3
  elif f=='P': # PSC Motor in Air Handler
    ANO = 17
    WCFM_C = 0.5
    WCFM_H = 0.5
  else:
    print "ERROR: Invalid Motor Type"
    return
  
  if t == 'w': # Wide setpoint range
    THhi = 70
    THlo = 70
    TChi = 77
    TClo = 77
  elif t == 'n': # Narrow temperature range
    THhi = 72
    THlo = 72
    TChi = 75
    TClo = 75
  else:
    print "ERROR: Invalid Temperature Range"
    return
  
# Dehumidifier
  DSET = 220
  DCFM = 220
  DSIM_OPT = 1
  Res_DNO = 3

  if s == 1: # Continuous exhaust ventilation
    fctyp5 = 0
    ftim_ON5 = 0
    ftim_OFF5 = 0
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 0
    fctyp8 = 1
    ilck81 = 0
    VCFM = 0
    fctyp9 = 0
    ilck91 = 0
    exh_cfm = vent0
    HRV_CFM = 0
  elif s == 2: # CFIS 33% min @ 62.2 no max
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 5
    fctyp8 = 0
    ilck81 = 0
    VCFM = vent0
    fctyp9 = 0
    ilck91 = 0
    exh_cfm = 0
    HRV_CFM = 0
  elif s == 3: # CFIS 33% @ 62.2 
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 4
    ftim_ON7 = 0.17
    ftim_OFF7 = 0.33
    ilck71 = 5
    fctyp8 = 0
    ilck81 = 0
    VCFM = vent0
    fctyp9 = 0
    ilck91 = 0
    exh_cfm = 0
    HRV_CFM = 0
  elif s == 4: # CFIS 33% min @ 3x62.2 no max
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 5
    fctyp8 = 0
    ilck81 = 0
    VCFM = 3*vent0
    fctyp9 = 0
    ilck91 = 0
    exh_cfm = 0
    HRV_CFM = 0
  elif s == 5: # CFIS 33% @ 3x 62.2
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 4
    ftim_ON7 = 0.17
    ftim_OFF7 = 0.33
    ilck71 = 5
    fctyp8 = 0
    ilck81 = 0
    VCFM = 3*vent0
    fctyp9 = 0
    ilck91 = 0
    exh_cfm = 0
    HRV_CFM = 0
  elif s == 6: # CFIS 33% min @ 62.2 w/ fill-in exhaust
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 5
    fctyp8 = 0
    ilck81 = -7
    fctyp9 = 0
    ilck91 = 0
    VCFM = vent0
    exh_cfm = vent0
    HRV_CFM = 0
  elif s == 7: # CFIS 33% min @ 62.2 w/ fill-in HRV
    fctyp5 = 4
    ftim_ON5 = 0.17
    ftim_OFF5 = 0.33
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 5
    fctyp8 = 0
    ilck81 = 0
    fctyp9 = 0
    ilck91 = -7
    VCFM = vent0
    exh_cfm = 0
    HRV_CFM = vent0
  elif s == 8: # 100% HRV
    fctyp5 = 0
    ftim_ON5 = 0
    ftim_OFF5 = 0
    fctyp6 = 0
    ilck61 = 3
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 0
    fctyp8 = 0
    ilck81 = 0
    fctyp9 = 1
    ilck91 = 0
    VCFM = 0
    exh_cfm = 0
    HRV_CFM = vent0
  else:
    print "ERROR: Invalid Ventilation System"
    return

  for Run, WeatherFile, SinZone_bno, ACTON, Zone in climate:
    ACTON = float(ACTON)
    if m == 'h':
      ACTON += 0.5
    elif m == 'o':
      ACTON += 1
    elif m == 'z':
      pass
    else:
      print "ERROR: Invalid AC Size"
      return

    if Zone in ['1', '2a', '3a']:
      HRV_eL = 0.6
    else:
      HRV_eL = 0

    ACCFM = 400*float(ACTON)
    Desc = ''.join([m,str(s),f,t,'-',WeatherFile])

    yield order_line(locals())

def single_city(site):
  clime = [el for el in climate if el[1]==site]
  filename = 'all-{0}.csv'.format(site)
  file = csv.writer(open(filename, 'w'))
  file.writerow(head)
  lcount = 0

  for m in ['z', 'h', 'o']:
    for f in ['E', 'P']:
      for t in ['w','n']:
        for s in xrange(1,9):
          for line in sim_lines(m,s,f,t,clime):
            lcount += 1
            line[head.index('Run')] = lcount
            file.writerow(line)
  print "%s lines in %s" % (lcount, filename)

def full_parametric():
  for m in ['z', 'h', 'o']:
    for f in ['E', 'P']:
      for t in ['w','n']:
        for s in xrange(1,9):
          filename = ''.join([m,str(s),f,t,'.csv'])
          file = csv.writer(open(filename, 'w'))
          file.writerow(head)
          lcount = 0
          for line in sim_lines(m,s,f,t,climate):
            lcount += 1
            file.writerow(line)
          print "%s lines in %s" % (lcount, filename)

def by_system(systems):
  for m in ['z', 'h', 'o']:
    for f in ['E', 'P']:
      for t in ['w','n']:
        for s in systems[:]:
          filename = ''.join([m,str(s),f,t,'.csv'])
          file = csv.writer(open(filename, 'w'))
          file.writerow(head)
          lcount = 0
          for line in sim_lines(m,s,f,t,climate):
            lcount += 1
            file.writerow(line)
          print "%s lines in %s" % (lcount, filename)

def sizing():
  filename = 'o1Ew.csv'
  file = csv.writer(open(filename, 'w'))
  file.writerow(head)
  lcount = 0
  for line in sim_lines('o', 1, 'E', 'w'):
    lcount += 1
    if lcount == 63:
       file = csv.writer(open('o1Ew.csv','w'))
       file.writerow(head)
    if lcount == 125:
       file = csv.writer(open('o1Ew.csv','w'))
       file.writerow(head)
    file.writerow(line)

by_system([6])
