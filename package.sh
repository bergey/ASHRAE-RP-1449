#!/usr/bin/sh
cp 1449.TRD package
cp TRN_Resdh4.py package
cp buildings/* package
cp lookups/* package
cp types/* package
cp res_dh_sched.dat package
rm -r package/sim-specs
cp -r sim-specs package
