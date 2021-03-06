import csv
from math import sqrt
import os

head = ['Desc', '', 'BaseFile', 'Run', 'SinZone_bno', 'WeatherFile', 'ELA', 'ACTON', 'ACCFM', 'ANO', 'Ht_QIN', 'HCFM', 'THhi', 'THlo', 'HUM_CNTL_type', 'Res_DNO', 'DCFM_AHU', 'DCFM_no_AHU', 'REGEN', 'DSIN_OPT', 'DSIN_VAL', 'RSCHD', 'DSOUT', 'Humlo_0', 'Humhi_0', 'WCFM_H', 'HRV_eS', 'HRV_eL', 'VCFM', 'exh_cfm', 'HRV_CFM', 'HRV_W', 'fctyp5', 'ftim_ON5', 'ftim_OFF5', 'fctyp7', 'ftim_ON7', 'ftim_OFF7', 'ilck71', 'fctyp8', 'fctyp9', 'ftim_ON9', 'ftim_OFF9', 'ilck91', 'sduct_area', 'rduct_area', 'leaks', 'leakr', 'duct_Rval', 'SENS_DAILY', 'LATG_DAILY']
run_index = head.index('Run')



SENS_BASE = 72700 # BTU/day
LATG_BASE = 12 # lbs/day

def order_line(d):
  try:
    return [d['Desc'],None]+[d[h] for h in head[2:]]
  except:
    print(d)
    raise

bno_file = open('../buildings/Single_Zone_Buildings.txt')
bno_lines = csv.reader(bno_file)
bno = dict()
bno_ct = next(bno_lines)[0] #  header (line count)
for line in bno_lines:
  bno[line[3].strip()] = line[0].strip()
bno_file.close()
if len(bno) != int(bno_ct):
  print("""you should update header of Single_Zone_Buildings to match contents
        length is {0}, header says {1}""".format(len(bno), bno_ct))

def get_bno(z,h):
  if z==0:
    building_zone=1
  else:
    building_zone=z
  return bno['z{0}h{1}.bui'.format(building_zone,h)]

def sf_by_size(sz):
  # for use in calculating ELA, infiltration
  if sz == 'sm':
    return 1198
  elif sz == 'md':
    return 2016
  elif sz == 'lg':
    return 3495
  else:
    raise UserWarning("Unknown size {0}".format(sz))

def recirc(cfm, sz):
    "return on-time (in hours) to provide 0.5 ACH"
    vol = 8*sf_by_size(sz)
    runtime =  0.5*vol/(60*cfm) # fraction of hour
    return (0.02*round(runtime/0.02)) # round to multiple of timestep

def ach_to_ela(ach, sz):
  v = sf_by_size(sz)*8 # volume
  n = 0.67
  cfm4 = v*ach/60*(4./50)**n
  cmps = cfm4/35.3147/60 # cubic meters per second at 4 Pa
  # leakage area, sq meters, assume discharge coefficient is 1
  sm = cmps * sqrt(1.2/2/4)/1
  ela = sm * (100/2.54)**2
  return ela

def hers_to_ach(h):
  if h==50:
    return 3
  elif h==70:
    return 4
  elif h==85:
    return 5
  elif h==100:
    return 7
  elif h==130:
    return 10
  else:
    raise

def gains_factor(sz):
  if sz == 'md':
    return 1
  elif sz == 'sm':
    return 2.0/3.0
  elif sz == 'lg':
    return 4.0/3.0
  else:
    raise UserWarning("Unknown house size: {0}".format(sz))

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
def sim_line(z,h,s,rh,v,sz):
  """sim_line takes the following parameters:
  - Climate Zone (0-5)
  - HERS level (50-130)
  - DH System (1-14)
  - RH Setpoint (50-60)
  - House Size (sm, md, lg)"""
# exclude unimplemented scenarios
  # no explicit rh control
  # don't use ERV in cold climates
  # or HRV in warm climates; z3 gets both
  # unventilated HERS 130, except system 1 comparison
#  if (rh==60 and s in [1, 3, 4]) or (v==3 and z>3) or (v==4 and z<3) or (h==130 and v!=0 and s!=1) or (v==0 and h!= 130 and s!=1)
  if (s==1 and rh==60) or (v==1 and h==130 and s!=1) or (v==2 and h==130) or (v in (3,4) and h==130) or (v in (3,4) and s in (6,7,9)) or (v==4 and z>3) or (v==3 and z<3):
     return None
     

  Run = 1 # update in enclosing code

  BaseFile = '1449.TRD'

  if sz == 'md':
    Desc = 'z{0}h{1}s{2}rh{3}v{4}'.format(z,h,s,rh,v)
  else:
    Desc = 'z{0}h{1}s{2}rh{3}v{4}-{5}'.format(z,h,s,rh,v,sz)
  
  SinZone_bno = get_bno(z,h)

  ELA = ach_to_ela(hers_to_ach(h), sz)

  vent0 = {'sm': 35, 'md': 58, 'lg': 73}[sz]
  
  WeatherFile = ['Orlando-FL-3', 'Miami-FL-3', 'Houston-TX-3', 'Atlanta-GA-3', 'Nashville-TN-3', 'Indianapolis-IN-3'][z]
  
  # vector is: Orlando, Miami, Houston, Atlanta, Nashville, Indianapolis
  hp_tonnage = {'md':{130: [3,3,3,2.5,2.5,2.5],
                      100: [3,3,3,2.5,2.5,2.5],
                       85: [2.5,2.5,2.5,2,2,2],
                       70: [2.5,2,2,2,2,2],
                       50: [2,2,2,2,2,2]},
                'sm':{130: [2.5,2.5,2,2,2,2],
                      100: [2.5,2.5,2.5,2,2,2],
                       85: [2,2,2,2,2,2],
                       70: [2,2,2,2,2,2],
                       50: [2,2,2,2,2,2]},
                'lg':{130: [4.5,4.5,4.5,4,3.5,3.5],
                      100: [4.5,4.5,4,3.5,3.5,3],
                       85: [3,3,3,3,2.5,2.5],
                       70: [2.5,2.5,2.5,2.5,2,2],
                       50: [2,2,2,2,2,2]}}

  ACTON = hp_tonnage[sz][h][z] # 0-indexed array, starting with Orlando

  ACCFM = ACTON*375

  if s==3:
    ANO = 19
  elif s==4:
    ANO = 20
  elif s==1 and h<85:
    ANO = 18
  elif s==12:
    ANO = {130: 21,
           100: 22,
            85: 23,
            70: 24,
            50: 24}[h]
  else:
    ANO = {130: 16,
           100: 17,
            85: 18,
            70: 19,
            50: 19}[h]

  if sz=='md' and (h<=70 or z<=1):
    Ht_QIN = 40000
  elif sz=='sm':
    Ht_QIN = 40000
  elif sz=='lg' and h==50:
    Ht_QIN = 40000
  elif sz=='lg' and h>=100 and z>1:
    Ht_QIN = 80000
  else:
    Ht_QIN = 60000
  
  HCFM = ACTON*275

  if z<= 2:
    THhi = 72
    THlo = 72
  else:
    THhi = 70
    THlo = 70

  if s==2:
    HUM_CNTL_type = 3
  elif s==8:
    HUM_CNTL_type = 5 # Lennox
  elif s==10:
    HUM_CNTL_type = 4
  elif s==11:
    HUM_CNTL_type = 2
  else:
    HUM_CNTL_type = 0 # no explicit DH Control by AC
  
  if s==5:
    Res_DNO = 21
  elif s==6:
    Res_DNO = 21 # TODO get new dh line
  elif s==7:
    Res_DNO = 21 # TODO get line for s7
  else:
    Res_DNO = 1
  
  if s==5:
    DCFM_AHU = 148
    DCFM_no_AHU = 148
  elif s==6:
    DCFM_AHU = 100
    DCFM_no_AHU = 120
  elif s==7:
    DCFM_AHU = 183
    DCFM_no_AHU = 220
  else:
    DCFM_AHU = 1 # cannot be zero or TRNSYS tries to divide by 0
    DCFM_no_AHU = 1
  
  REGEN = 0 # TODO where does this change?
  
  if s==7:
    DSIN_OPT = 2
    DSIN_VAL = 0.67 # 2:1, mostly recirc
  else:
    DSIN_OPT = 1
    DSIN_VAL = 0 # not used
    
  RSCHD = 0
  
  DSOUT = 1
  
  if s in [1, 3, 4]:
    Humlo_0 = 99
    Humhi_0 = 99
  else:
    Humlo_0 = rh
    Humhi_0 = rh
    
  if h<=85:
    WCFM_H = 0.35
  else:
    WCFM_H = 0.5

  if v==3:
    HRV_eS = 0.75
    HRV_eL = 0
  elif v==4:
    HRV_eS = 0.7
    HRV_eL = 0.6
  else:
    HRV_eS = 0
    HRV_eL = 0

  if v==2:
    VCFM = vent0*3
  else:
    VCFM = 0

  if v==1:
    exh_cfm = vent0
  else:
    exh_cfm = 0
  
  if v==3 or v==4:
    HRV_CFM = 2*vent0 # twice 62.2 for 50% of hour
    HRV_W = 0.5*HRV_CFM # 0.5 W/CFM per Task 4 report
  else:
    HRV_CFM = 0
    HRV_W = 0
    
  if v==2:
    fctyp5 = 3  # AHU fan cycling
    ftim_ON5 = 0.17 # 33% of hour, two cycles per hour
    ftim_OFF5 = 0.33
  elif v==3 or v==4:
    fctyp5 = 3
    ftim_ON5 = 0.5  # concurrent with HRV
    ftim_OFF5 = 0.5
  elif s in [5, 6, 7]:
    fctyp5 = 3
    ftim_ON5 = recirc(ACCFM, sz)
    ftim_OFF5 = 1 - ftim_ON5
  else:
    fctyp5 = 0
    ftim_ON5 = 0
    ftim_OFF5 = 0
    
  if v==2:
    fctyp7 = 5
    ilck71 = 5
    ftim_ON7 = 0.17
    ftim_OFF7 = 0.33
  elif s==7: # never when v==2
    fctyp7 = 5
    ilck71 = 3
    ftim_ON7 = vent0 / (DCFM_no_AHU * (1-DSIN_VAL)) # on time to achieve 62.2
    ftim_OFF7 = 1 - ftim_ON7
  else:
    fctyp7 = 0
    ilck71 = 0
    ftim_ON7 = 0
    ftim_OFF7 = 0
    
  if v==1:
    fctyp8 = 1
  else:
    fctyp8 =  0

  if v==3 or v==4:
    fctyp9 = 5
    ftim_ON9 = 0.5
    ftim_OFF9 = 0.5
    ilck91 = 5
  else:
    fctyp9 = 0
    ftim_ON9 = 0.0
    ftim_OFF9 = 0.0
    ilck91 = 0


  if s==4 or h==50: # minisplits or ducts inside
    duct_area = 0
  elif h==70: # reduced attic duct area in cold zones
      if sz=='md':
          sduct_area = [544, 544, 544, 544, 250, 100][z]
      elif sz=='sm':
          sduct_area = [325, 325, 325, 325, 150, 65][z]
      elif sz=='lg':
          sduct_area = [945, 945, 945, 945, 475, 180][z]
  else:
    sduct_area = {'md':544, 'sm': 325, 'lg': 945}[sz]

  if s==4 or h==50:
    rduct_area = 0
  else:
    rduct_area = 100

  if s==4:
    leaks = 0
    leakr = 0
  else:
    leaks, leakr = { 50: (0,0),
                     70: (0.03, 0.02),
                     85: (0.03, 0.02),
                    100: (0.06, 0.04),
                    130: (0.12, 0.08) }[h]
  if s==4 or h==50:
    duct_Rval = 1
  elif h<=85:
    duct_Rval = 8
  else:
    duct_Rval = 6

  SENS_DAILY = gains_factor(sz)*SENS_BASE*{130: 1,
                                           100: 1,
                                           85: 0.9,
                                           70: 0.8,
                                           50: 0.7}[h]
  
  LATG_DAILY = gains_factor(sz)*LATG_BASE


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
  print("{0} lines in {1}".format(lcount, filename))

def full_parametric():
  for h in [50, 70, 85, 100, 130]:
    filename = "hers{0}.csv".format(h)
    file = csv.writer(open(filename, 'w'))
    file.writerow(head)
    lcount = 0
    for z in range(1,6):
      for s in range(1, 15):
        for rh in [50, 60]:
          for v in [0, 1, 2, 3, 4]:
            lcount += 1
            row = sim_line(z,h,s,rh,v)
            if row:
              row[head.index('Run')] = lcount + 1
              file.writerow(row)
      print("{0} lines in {1}".format(lcount, filename))


def by_system(systems):
  for s in systems:
    lcount = 0
    #filename = "s{0}h{1}v{2}.csv".format(s,h,v)
    filename = "s{0}.csv".format(s)
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for h in [50, 70, 85, 100, 130]:
      for v in [0, 1, 2, 3, 4]:
        for z in range(0,6):
          for rh in [50, 60]:
            row = sim_line(z,h,s,rh,v)
            if row:
              lcount += 1
              row[head.index('Run')] = lcount
              out_csv.writerow(row)
    if lcount==0:
            handle.close()
            os.remove(filename)
    else:
                  print("{0} lines in {1}".format(lcount, filename))

def just_one(z, h, s, rh, v):
  filename = 'z{0}h{1}s{2}v{3}rh{4}.csv'.format(z,h,s,v,rh)
  row = sim_line(z,h,s,rh,v)
  if row:
    file = csv.writer(open(filename, 'w'))
    file.writerow(head)
    file.writerow(sim_line(z,h,s,rh,v))
  else:
    print("No run planned for {0}".format(filename))

def debug_runs():
    lcount = 0
    filename = 'z1s1.csv'
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for h in [50, 85, 100, 130]:
        for v in [0, 1]:
            for z in range(0,2):
                row = sim_line(z, h, 1, 50, v)
                if row:
                    lcount += 1
                    row[head.index('Run')] = lcount
                    out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))

def short(*systems):
  for s in systems:
    lcount = 0
    filename = 's{0}_short.csv'.format(s)
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for v in xrange(5):
      row = sim_line(1, 100, s, 50, v)
      if row:
        lcount += 1
        row[head.index('Run')] = lcount
        out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))


def thhi_72():
  for s in [1,3, 4,5]:
    lcount = 0
    filename = 'thhi-s{0}.csv'.format(s)
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for z in xrange(3):
      for h in [50, 70, 85, 100, 130]:
        for v in xrange(5):
          for rh in [50, 60]:
            row = sim_line(z, h, s, rh, v)
            if row:
              lcount += 1
              row[head.index('Run')] = lcount
              out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))

def sys_10_11():
  # cf Task 4 report pg 32
  # should be 48 simulations in this set (24 for each system)
  for s in [10, 11]:
    lcount = 0
    filename = 's{0}.csv'.format(s)
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for z in [2, 4]:
      for h in [70, 100]:
        for v in [1, 2, 3, 4]:
          for rh in [50, 60]:
            row = sim_line(z, h, s, rh, v)
            if row:
              lcount += 1
              row[head.index('Run')] = lcount
              out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))

def sys_12_13_14():
# cf Task 4 report pg 32
  # should be 28 simulations in this set
  for s in [12]: # [12, 13, 14]
    lcount = 0
    filename = 's{0}.csv'.format(s)
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for h in [70, 100]:
      for v in [1, 2, 4]:
        for rh in [50, 60]:
          row = sim_line(2, h, s, rh, v)
          if row:
            lcount += 1
            row[head.index('Run')] = lcount
            out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))


def sensitivity_size():
    lcount = 0
    filename = 'size.csv'
    handle = open(filename, 'w')
    out_csv = csv.writer(handle)
    out_csv.writerow(head)
    for sz in ['sm', 'md', 'lg']:
        for s in [1,6]:
            for h in [70,100]:
                for z in [2,4]:
                    for rh in [50, 60]:
                        for v in [1,2,3,4]:
                            row = sim_line(z,h,s,rh,v,sz)
                            if row:
                                lcount += 1
                                row[head.index('Run')] = lcount
                                out_csv.writerow(row)
    print("{0} lines in {1}".format(lcount, filename))


# by_system([1,2,3,4,5,6,7,8])
# sys_10_11()
#sys_12_13_14()
#short(1, 2, 3, 4, 5, 6,7,8,)
sensitivity_size()
