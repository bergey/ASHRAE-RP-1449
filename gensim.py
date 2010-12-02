import csv

head = ['Desc','','BaseFile','Run','SinZone_bno','WeatherFile','ACTON','ACCFM','ANO','WCFM_C','WCFM_H','THhi','THlo','TChi','TClo','fctyp5','ftim_ON5','ftim_OFF5','fctyp6','ilck61','fctyp7','ftim_ON7','ftim_OFF7','ilck71','fctyp8','ilck81','fctyp9','ilck91','VCFM','exh_cfm','Res_DNO','DSET','DCFM','DSIM_OPT', 'HRV_CFM', 'HRV_eL']


vent0 = 58 # cfm, 62.2 rate, 2016 sf, 4 bedrooms

def order_line(d):
  return [d['Desc'],None]+[d[h] for h in head[2:]]

def sim_lines(m,s,f,t,climate):
  BaseFile = 'BSC-008.trd'
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

just_one(z=1, h=50, s=1, v=1, r=50)
