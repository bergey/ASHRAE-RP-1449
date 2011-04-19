import numpy as np

fields = [('year', 'u2',2,3), ('month', 'u2',4,5), ('day', 'u2',6,7), ('hour', 'u2',8,9), 
         ('ext_horiz', 'u2',10,13), ('ext_direct', 'u2',14,17), 
         ('horiz', 'u2',18,21), ('dir_normal', 'u2',24,27), ('diff_horiz', 'u2',30,33), 
         ('horiz_lux', 'u2',36,39), ('dir_normal_lux', 'u2',42,45), ('diff_horiz_lux', 'u2',48,51),
         ('zenith_lum', 'u2',54,57), ('sky_cover', 'u1',60,61), ('sky_opaque', 'u1',64,65), 
         ('dry_bulb', 'f4', 68,71), ('dew_point', 'f4', 74,77), ('rel_humid', 'u1', 80,82),
         ('p_atm', 'u2', 85,88), ('wind_dir', 'u2', 91,93), ('wind_speed', 'u2', 96,98),
         ('visibility', 'u2', 101, 104), ('ceiling', 'u4', 107,111)]
# NB: Not complete
# Need to fill in some variables
# Probably will not expose data source or uncertainty
dtype = [el[:2] for el in fields]

def weather(handle, format='tmy2'):
    #print dtype
    ret = np.zeros(8760, dtype)
    handle.next()
    for i, line in enumerate(handle):
        for j, field in enumerate(fields):
            name, t, l, r = field
            #print i, name
            if name in ['dry_bulb', 'dew_point']:
                ret[i][j] = float(line[l-1:r])/10
            else:
                ret[i][j] = int(line[l-1:r])
    return ret
