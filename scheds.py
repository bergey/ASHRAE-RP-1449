sens5 = [2182,2084,2033,2029,2327,3101,3727,3652,2456,2026,1952,1907,1853,1802,1799,2124,3028,4321,5321,5561,5527,4576,3477,2722]

sens2 = [2182,2084,2033,2029,2327,3107,3712,3808,2888,2454,2380,2335,2281,2231,2228,2481,3485,4321,5028,5318,5237,4771,3765,2722]

latg5 = [766,751,738,739,757,829,973,911,526,389,358,354,345,315,305,336,429,834,1115,1000,945,914,856,811]

latg2 = [766,751,738,739,757,829,973,1024,778,638,607,603,595,565,554,585,791,947,896,781,726,914,856,811]

occ5 = [ 1.000,1.000,1.000,1.000,1.000,1.000,1.000,0.830,0.290,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.500,1.000,1.000,1.000,1.000,1.000,1.000]

occ2 = [1.000,    1.000,    1.000,    1.000,    1.000,    1.000,    1.000,    1.000,    0.670,    0.500,    0.500,    0.500,    0.500,    0.500,    0.500,    0.500,    0.670,    0.670,    0.670,    0.670,    0.670,    1.000,    1.000,    1.000]

sens_avg = ( 5 * sum(sens5) + 2 * sum(sens2) ) / 7.0
latg_avg = ( 5 * sum(latg5) + 2 * sum(latg2) ) / 7.0

for name, hours, avg in zip(['Weekday_Sensible', 'Weekend_Sensible', 'Weekday_Latent', 'Weekend_Latent'], [sens5, sens2, latg5, latg2], [sens_avg, sens_avg, latg_avg, latg_avg]):
  fout = open(name, 'wb')
  fout.writelines([name, '\n'])
  for i, h in enumerate(hours):
    p = hours[(i-1)%24] # previous hour (% not actually needed)
    n = hours[(i+1)%24] # next hour
    d0 = h
    d1 = (n-p)/2
    d2 = n+p-2*h
    for t in map( (lambda x: x/100.0), range(-50,50,2)):
      BTUs = d2*t**2 + d1*(t+0.5) + d0 - (d2/12 + d1/2)
      str_out = '{0:.5}\n'.format(BTUs/avg)
      fout.write(str_out)
  fout.close()

for name, hours in zip(['Weekday_Occupancy', 'Weekend_Occupancy'], [occ5, occ2]):
  fout = open(name, 'wb')
  fout.writelines([name, '\n'])
  for h in hours:
    for t in xrange(50):
      fout.write('{0:.3}\n'.format(h))
