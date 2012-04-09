from numpy import loadtxt, nan
from datetime import datetime
import csv
import sys

filepath = '/home/bergey/bsc/dh/references/aaon-one-minute.csv'

class Empty:
    pass

# Full set of headers, for copy and paste
# "TIMESTAMP"
# "RECORD"
# "T_Amb1_C_AVG"
# "T_Amb2_C_AVG"
# "T_HumAmb_C_AVG"
# "RH_HumAmb_frc_AVG"
# "I_Horiz_Wm2_AVG"
# "EE_House_kWh_TOT"
# "EE_HP_kWh_TOT"
# "EE_AH_kWh_TOT"
# "EE_DHW_kWh_TOT"
# "EE_StrHeat_kWh_TOT"
# "T_Refrig1_C_AVG"  # Evap inlet
# "T_Refrig2_C_AVG"  # Evap Exit
# "T_Extra1_C_AVG"   # Reheat inlet
# "T_Extra2_C_AVG"   # Reheat outlet
# "T_Extra3_C_AVG" # Outdoor T
# "T_Extra4_C_AVG"
# "T_Extra5_C_AVG"
# "T_1stFloor1_C_AVG"
# "T_1stFloor2_C_AVG"
# "T_2ndFloor1_C_AVG"
# "T_2ndFloor2_C_AVG"
# "T_AHreturn_C_AVG"
# "T_AHsupply1_C_AVG"
# "T_AHsupply2_C_AVG"
# "RH_1stFlr1_frc_AVG"
# "RH_1stFlr2_frc_AVG"
# "RH_2ndFlr1_frc_AVG"
# "RH_2ndFlr2_frc_AVG"
# "RH_AHretrn_frc_AVG"
# "RH_AHsupp1_frc_AVG"
# "RH_AHsupp2_frc_AVG"
# "P_Refrig1_kPa_AVG"
# "P_Refrig2_kPa_AVG"
# "F_Condensate_l_TOT"
# "F_TipBucket_l_TOT"
# "Stat_HPheat_AVG"
# "Stat_CoolStg1_AVG"
# "Stat_CoolStg2_AVG"
# "Stat_Dehum_AVG"
# "Stat_DehDisabl_AVG"
# "Stat_G_AVG"n
# "Stat_HP_AVG"
# "Stat_AH_AVG"
# "Stat_DHW_AVG"
# "Stat_StrHeat1_AVG"
# "Stat_StrHeat2_AVG"
# "Cycles_HP_0001"
# "Cycles_AH_0001"
# "Cycls_DHW_0001"
# "Cycls_SH1_0001"
# "Cycls_SH2_0001"
# "EP_HP_kW_AVG"
# "EP_AH_kW_AVG"
# "EP_DHW_kW_AVG"
# "EP_StrHeat_kW_AVG"
# "EP_StrHeat_kW_AVG~2"
# "T_Refrig1_C_AVG~2"
# "T_Refrig2_C_AVG~2"
# "T_ref_C_AVG"
# "T_logger_C_AVG"
# "V_logger_V_AVG"

aaon_columns = [("TIMESTAMP", 't'),
                ("T_Amb1_C_AVG", 'Tamb'),
                ("RH_HumAmb_frc_AVG", 'RHamb'), 
                ("T_AHreturn_C_AVG", 'Tret'), 
                ("T_AHsupply1_C_AVG", 'Tsup'),
                ("RH_AHretrn_frc_AVG", 'RHret'), 
                ("RH_AHsupp1_frc_AVG", 'RHsup'), 
                ("Stat_HPheat_AVG", 'Sht'),
                ("Stat_CoolStg1_AVG", 'Sc1'),
                ("Stat_CoolStg2_AVG", 'Sc2'),
                ("Stat_Dehum_AVG", 'Sdh'),
                ("Stat_DehDisabl_AVG", 'Sdd'),
                ("Stat_AH_AVG", 'Sah'),
                ("EP_HP_kW_AVG", 'kWhp'),
                ("EP_AH_kW_AVG", 'kWah'),
                ("T_Refrig1_C_AVG", 'Tr1'), # outdoor coil
                ("T_Refrig2_C_AVG", 'Tr2'), # indoor coil, heated by return air
                ("T_Extra1_C_AVG", 'Te1'), # reheat coil
                ("T_Extra2_C_AVG", 'Te2'),
#                ("T_Extra3_C_AVG",
 #               ("T_Extra4_C_AVG",
  #              ("T_Extra5_C_AVG",
                ("P_Refrig1_kPa_AVG", 'Pev_i'), # inlet outdoor
                ("P_Refrig2_kPa_AVG", 'Pev_o'), # outlet outdoor
                ("F_TipBucket_l_TOT", 'cond'),
                ("RH_1stFlr1_frc_AVG", 'RH1'),
                ("T_1stFloor1_C_AVG", 'T1') ]


def inf_to_nan(x):
    if x == '"INF"':
        return nan
    else:
        return float(x)

def aaon_converters(head):
    by_name = {"TIMESTAMP": lambda d: float(datetime.strptime(d, '"%Y-%m-%d %H:%M:%S"').strftime('%Y%j%H%M%S')),
               "EP_HP_kW_AVG": inf_to_nan,
               "EP_AH_kW_AVG": inf_to_nan,}
    # replace key in by_name by column index
    return dict( [ (head.index(name), function) for name, function in by_name.items()] )

def load_aaon(lo, hi):
    # read column names from first row, to avoid hardcoded, hard-to-read indices
    fin = open(filepath)
    reader = csv.reader(fin)
    head = reader.next()
    fin.close()

    unlabeled= loadtxt(filepath,
                   delimiter=',',
                   converters = aaon_converters(head),
                   skiprows = 3,
                   usecols = [head.index(c) for (c,n) in aaon_columns])
    labeled = Empty()
    for i, (col, name) in enumerate(aaon_columns):
        labeled.__dict__[name] = unlabeled[lo:hi,i]
    return labeled

if __name__ == '__main__':
    print("loading data")
    a = load_aaon(0,1083438)
    #a = load_aaon(470000,1083438)

    # cndn = ((a.Stat_Dehum_AVG==0) & (a.Stat_CoolStg1_AVG==0))
    # cydn = ((a.Stat_Dehum_AVG==0) & (a.Stat_CoolStg1_AVG==1))
    # cydy = ((a.Stat_Dehum_AVG==1) & (a.Stat_CoolStg1_AVG==1))
    # cndy = ((a.Stat_Dehum_AVG==1) & (a.Stat_CoolStg1_AVG==0))

    
