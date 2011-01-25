#!/usr/bin/sh
rsync -v 1449.TRD package
rsync -v TRN_Resdh4.py package
rsync -v buildings/* package
rsync -v lookups/* package
rsync -v res_dh_sched.dat package
rsync -vr package /mnt/flash/package
