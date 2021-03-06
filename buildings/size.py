import re
import os

lookup = open('size sensitivity.txt', 'w')
n = 112 # first n to add
# for z in [1,2,3,4,5]:
#   for h in [50, 70, 85, 100, 130]:
#     fname = "z{0}h{1}.bui".format(z,h)
#     med = open(fname).read()
    
#     sm = re.sub(r'187.3', '111.35', med)  # floor area
#     sm = re.sub(r'36.64', '25.57', sm)   # N/S walls (net windows)
#     sm = re.sub(r'23.56', '16.59', sm)   # E/W walls
#     sm = re.sub(r'10.18', '6.39', sm)    # N/S windows
#     sm = re.sub(r'6.54 :', '4.15 :', sm) # E/W windows
#     sm = re.sub(r'12331.2', '6521', sm)  # heat capacity
#     sm = re.sub(r'456.7', '271.69', sm)  # air volume
#     sm = re.sub(r'101.45', '60.3', sm)   # roof area
#     sm = re.sub(r'12.54', '7.5', sm)     # gable area
#     smname = "{0}-sm.bui".format(fname[:-4])
#     open(smname, 'w').write(sm)
#     name = '{n},{n}-Zone {z} HERS {h} (z{z}h{h}-sm.bui)'.format(n=n,h=h,z=z)
#     lookup.write('{name: <78}, 8,{smname: >26}, 1198, 1, 0, 0.495, 8,   3,0,  0, 0\n'.format(name=name, smname=smname))
#     n += 1

#     lg = re.sub(r'187.3', '324.8', med)  # floor area
#     lg = re.sub(r'36.64', '43.72', lg)   # N/S walls (net windows)
#     lg = re.sub(r'23.56', '28.30', lg)   # E/W walls
#     lg = re.sub(r'10.18', '10.93', lg)    # N/S windows
#     lg = re.sub(r'6.54 :', '7.08 :', lg) # E/W windows
#     lg = re.sub(r'12331.2', '19020', lg)  # heat capacity
#     lg = re.sub(r'456.7', '792.51', lg)  # air volume
#     lg = re.sub(r'101.45', '175.9', lg)   # roof area
#     lg = re.sub(r'12.54', '21.9', lg)     # gable area
#     lgname = "{0}-lg.bui".format(fname[:-4])
#     open(lgname, 'w').write(lg)
#     name = '{n},{n}-Zone {z} HERS {h} (z{z}h{h}-lg.bui)'.format(n=n,h=h,z=z)
#     lookup.write('{name: <78}, 8,{lgname: >26}, 3495, 1, 0, 0.495, 8,   4,0,  0, 0\n'.format(name=name, lgname=lgname))
#     n += 1
# Only control cases medium
for z in [2,4]:
  for h in [70,100]:
    fname = "z{0}h{1}.bui".format(z,h)
    old = open(fname).read()
    
    new = re.sub(r'187.3', '188.1', old)  # floor area
    new = re.sub(r'36.64', '33.38', new)   # N/S walls (net windows)
    new = re.sub(r'23.56', '21.47', new)   # E/W walls
    new = re.sub(r'10.18', '8.34', new)    # N/S windows
    new = re.sub(r'6.54 :', '5.37 :', new) # E/W windows
    new = re.sub(r'12331.2', '11015', new)  # heat capacity
    new = re.sub(r'456.7', '458.96', new)  # air volume
    new = re.sub(r'101.45', '101.9', new)   # roof area
    new = re.sub(r'12.54', '12.6', new)     # gable area
    newname = "{0}-rev.bui".format(fname[:-4])
    open(newname, 'w').write(new)
    name = '{n},{n}-Zone {z} HERS {h} (z{z}h{h}-rev.bui)'.format(n=n,h=h,z=z)
    lookup.write('{name: <78}, 8,{newname: >26}, 2024, 1, 0, 0.495, 8,   3,0,  0, 0\n'.format(name=name, newname=newname))
    n += 1
