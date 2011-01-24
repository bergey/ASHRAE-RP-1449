import csv
from math import sqrt

head = ['Desc', '', 'BaseFile', 'Run', 'SinZone_bno', 'WeatherFile', 'ELA', 'ACTON', 'ACCFM', 'ANO', 'HCFM', 'HUM_CNTL_type', 'Res_DNO', 'DSET', 'Humlo_0', 'Humhi_0', 'WCFM_H', 'HRV_eS', 'HRV_eL', 'VCFM', 'exh_cfm', 'HRV_CFM', 'HRV_W', 'fctyp5', 'ftim_ON5', 'ftim_OFF5', 'fctyp7', 'ftim_ON7', 'ftim_OFF7', 'ilck71', 'fctyp8', 'fctyp9', 'ftim_ON9', 'ftim_OFF9', 'ilck91', 'sduct_area', 'rduct_area', 'leaks', 'leakr', 'duct_Rval', 'SENS_DAILY', 'LATG_DAILY']
run_index = head.index('Run')


vent0 = 58 # cfm, 62.2 rate, 2016 sf, 4 bedrooms
# TODO adjust vent for different house sizes in parametric
SENS_BASE = 72700 # 
LATG_BASE = 16.9 # lbs/day 

def order_line(d):
  return [d['Desc'],None]+[d[h] for h in head[2:]]

bno_file = open('../buildings/Single_Zone_Buildings.txt')
bno_lines = csv.reader(bno_file)
bno = dict()
bno_lines.next() # drop header (line count)
for line in bno_lines:
  bno[line[3].strip()] = line[0].strip()
bno_file.close()

def get_bno(z,h):
  return bno['z{0}h{1}.bui'.format(z,h)]

def ach_to_ela(ach):
  v = 2016*10 # volume
  n = 0.67
  cfm4 = v*ach/60*(4./50)**n
  cmps = cfm4/35.3147/60 # cubic meters per second at 4 Pa
  # leakage area, sq meters, assume discharge coefficient is 1
  sm = cmps * sqrt(1.2/2/4)/1 
  ela = sm * (100/2.54)**2
  return ela

# simulations are parameterized as follows:
# z zone 1--5
# 
# h HERS rating (50, 70, 85, 100, 130
#
# s system number from Task 4 report
#
# rh RH setpoint (50, 60)
#
# v ventilation system
#   1: exhaust only
#   2: CFIS
#   3: HRV / ERV
#
# Plan to refactor sim_lines to run the parametrics
# which alter:
#   building size
#   CFM/ton
#   duct leakage
#   duct insulation
#   ventilation rate
#   moisture generation
#   add heat pipe or dessicant unit
def sim_line(z,h,s,rh,v):
# exclude unimplemented scenarios
  if s != 1:
    return None
  if h <= 70:
    return None

  Run = 1 # update in enclosing code
  BaseFile = '1449.TRD'
  Desc = 'z{0}h{1}s{2}rh{3}v{4}'.format(z,h,s,rh,v) # TODO add more parameters
  SinZone_bno = get_bno(z,h)

  LATG_DAILY = LATG_BASE

# parameters depending only on HERS
  if h==50:
    ELA = ach_to_ela(3)
    # TODO SEER
    # TODO EER
    # HSPF in post-processing
    WCFM_H = 0.35
    SENS_DAILY = SENS_BASE*0.7
    sduct_area = 0
    rduct_area = 0
    leaks = 0
    leakr = 0
    duct_Rval = 1
  elif h==70:
# TODO punt for now
    pass
  elif h==85:
    ELA = ach_to_ela(5)
    WCFM_H = 0.35
    SENS_DAILY = SENS_BASE*0.9
    sduct_area = 544
    rduct_area = 100
    leaks = 0.03 # 5% total leakage, split 60/40
    leakr = 0.02
    duct_Rval = 8
  elif h==100:
    ELA = ach_to_ela(7)
    WCFM_H = 0.5
    SENS_DAILY = SENS_BASE
    sduct_area = 544
    rduct_area = 100
    leaks = 0.06 # 10% total
    leakr = 0.04
    duct_Rval = 6
  elif h==130:
    ELA = ach_to_ela(10)
    WCFM_H = 0.5
    SENS_DAILY = SENS_BASE
    sduct_area = 544
    rduct_area = 100
    leaks = 0.12
    leakr = 0.08
    duct_Rval = 6
  else:
    print("Shouldn't get here: HERS {0}".format(h))
    return None

  hp_tonnage = [[3,3,2.5,2,2],
                [3,3,2.5,2,2],
                [2.5,2.5,2,2,2],
                [2.5,2.5,2,2,2],
                [2.5,2.5,2,2,2]]
  hp_tonnage = {130: [3,3,2.5,2.5,2.5],
                100: [3,3,2.5,2.5,2.5],
                 85: [2.5,2.5,2,2,2],
                 70: [2,2,2,2,2],
                 50: [2,2,2,2,2]}
  ACTON = hp_tonnage[h][z-1] # 0-indexed array

# parameters depending on zone, or zone and HERS
  if z==1:
    WeatherFile = 'Miami-FL'
    HRV_eS = 0.7
    HRV_eL = 0.6
  elif z==2:
    WeatherFile = 'Houston-TX'
    HRV_eS = 0.7
    HRV_eL = 0.6 
  elif z==3:
    WeatherFile = 'Atlanta-GA'
    HRV_eS = 0.7 # TODO also run with HRV
    HRV_eL = 0.6
  elif z==4:
    WeatherFile = 'Nashville-TN'
    HRV_eS = 0.75
    HRV_eL = 0
  elif z==5:
    WeatherFile = 'Indianapolis-IN'
    HRV_eS = 0.75
    HRV_eL = 0

# parameters depending only on DH system
  if s==1:
    if rh == 60: 
      return None # no RH setpoint for system 1
    if h < 85:
      return None
    elif h==85: # XXX Can this move to HERS section above?
      ANO = 18
    elif h==100:
      ANO = 17
    elif h==130:
      ANO = 16
    #ACTON = 2 
    ACCFM = ACTON*375
    HCFM = ACTON*275
    HUM_CNTL_type = 0  # No enhanced DH
    # turn off standalone dehumidifier
    Res_DNO = 1
    ilck61 = 0
    Humlo_0 = 99
    Humhi_0 = 99
    DSET = 0 # TODO decide on units (SCFM or pints/day)
  else:
    Humlo_0 = rh
    Humhi_0 = rh

# TODO check DH air sources (should be same for all systems w/ DH)

  
# Ventilation systems
  if v==0: # No ventilation
    if h != 130 and s != 7:
      return None
    VCFM = 0
    exh_cfm = 0
    HRV_CFM = 0
    HRV_W = 0
    fctyp5 = 0
    ftim_ON5 = 0
    ftim_OFF5 = 0
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 0
    fctyp8 = 0
    fctyp9 = 0
    ftim_ON9 = 0.0
    ftim_OFF9 = 0.0
    ilck91 = 0
  elif v==1: # Exhaust only
    if h == 130:
      return None
    VCFM = 0
    exh_cfm = vent0
    HRV_CFM = 0
    HRV_W = 0
    fctyp5 = 0
    ftim_ON5 = 0
    ftim_OFF5 = 0
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 0
    fctyp8 = 1
    fctyp9 = 0
    ftim_ON9 = 0.0
    ftim_OFF9 = 0.0
    ilck91 = 0
  elif v==2: # CFIS
    if h == 130:
      return None
    VCFM = vent0
    exh_cfm = 0
    HRV_CFM = 0
    HRV_W = 0
    fctyp5 = 3
    ftim_ON5 = 0.17 # 33% of hour, two cycles per hour
    ftim_OFF5 = 0.33
    fctyp7 = 5
    ftim_ON7 = 0.17
    ftim_OFF7 = 0.33
    ilck71 = 5
    fctyp8 = 0
    fctyp9 = 0
    ftim_ON9 = 0.0
    ftim_OFF9 = 0.0
    ilck91 = 0
  elif v==3: # HRV
    if h == 130 or s in [5,6,7,9]:
      return None
    VCFM = 0
    exh_cfm = 0
    HRV_CFM = 2*vent0 # twice 62.2 for 50% of hour
    HRV_W = 0.5*HRV_CFM # 0.5 W/CFM per Task 4 report
    fctyp5 = 3
    ftim_ON5 = 0.5 # concurrent with HRV
    ftim_OFF5 = 0.5
    fctyp7 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    ilck71 = 0
    fctyp8 = 0
    fctyp9 = 5
    ftim_ON9 = 0.5
    ftim_OFF9 = 0.5
    ilck91 = 5

# put all of the variables used above into a list in a consistent order
  return order_line(locals())


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
  for h in [50, 70, 85, 100, 130]:
    filename = "hers{0}.csv".format(h)
    file = csv.writer(open(filename, 'w'))
    file.writerow(head)
    lcount = 0
    for z in range(1,6):
      for s in range(1, 15):
        for rh in [50, 60]:
          for v in [0, 1, 2, 3]:
            lcount += 1
            row = sim_line(z,h,s,rh,v)
            if row:
              row[head.index('Run')] = lcount + 1
              file.writerow(row)
    print "%s lines in %s" % (lcount, filename)

def by_system(systems):
  for s in systems:
    for h in [50, 70, 85, 100, 130]:
      for v in [0, 1, 2, 3]:
        lcount = 0
        filename = "s{0}h{1}v{2}.csv".format(s,h,v)
        file = csv.writer(open(filename, 'w'))
        file.writerow(head)
        for z in range(1,6):
          for rh in [50, 60]:
            row = sim_line(z,h,s,rh,v)
            if row:
              lcount += 1
              row[head.index('Run')] = lcount
              file.writerow(row)
        print "%s lines in %s" % (lcount, filename)

def just_one(z, h, s, rh, v):
  filename = 'z{0}h{1}s{2}v{3}rh{4}.csv'.format(z,h,s,v,rh) 
  row = sim_line(z,h,s,rh,v)
  if row:
    file = csv.writer(open(filename, 'w'))
    file.writerow(head)
    file.writerow(sim_line(z,h,s,rh,v))
  else:
    print "No run planned for {0}".format(filename)

by_system([1])
