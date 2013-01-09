c$DEBUG
      subroutine type140 (time,xin,out,t,dtdt,par,info,icntrl,*)
c*******************************************************************************
c                       *** Basic AC unit ***
c
c     This subroutine simulates: 
c		1) an AC unit using DOE_AC (via AC_HP)  or 
c         2) a chilled water coil based on CCDET from HVAC toolkit
c     This subroutine calls:  AC_HP from the library GRIAC. 
c       Shirey (8/31/90),(11/19/90),(11/27/90)
c       Henderson (12/5/90)
c       HH 1/24/91 -- added AC_DES & bypass option
c       HH 2/7/91 -- updated fan watts w/ bypass option
c       HH 2/19/91 -- added SHR correlation for CONST fan
c       HH 2/26/91 -- added control for heat pipes and des wheel (jbpON)
c       HH 3/1/91  -- added Tadp as output
c       HH 3/5/91  -- if ipflag > 100, start printing at that time
c       HH 9/27/94 -- added CWCOIL, updated SHR correlation
c       HH 10/3/94 -- corrected SHR correlation
c       HH 10/13/94 -- added additional SHR correlation
c       HH 10/14/94 -- added cwcoil adjustments (iac=5)
c       HH 11/11/94 -- modfied FSHR to vary twet,gamma for HPs
c       HH 1/15/95  -- added automatic corrections to twet/gamma for DX
c       HH 2/3/95  -- added twet/gamma for CW coil
c       HH 2/9/95  -- corrected error for twet/gamma w/ CW coil
c       HH 3/30/94 -- Capped Twet at 1200 sec to solve CW convergence problems
c	  KLS 11/18/05 -- Added Logic for Charge Ratio
C       HH,kbk 02/6/06 -- DOE_AC coeficients are read from file DOE_AC.cof
C       HH,kbk 02/8/06 -- Added part load performance correction
c	  HH 08/30/06   -- reinstated des_whl routine.  Now activated when ihp<0
c       HH 02/22/07   -- using jbpON => 2 to activate dehumidification mode
c					   for Lennox Humiditrol unit (1=bypass control, as before)
c	  HH 04/30/08 -- added capability to work in small timestep mode, The new inputs xin(11) and xin(12)
c					are used as the on-time/off-time.  In this case capacity is 
c					modified by time constant, evaporation occurs during off-cycle.  
c					SS part load is disabled
c       HH 10/31/10 -- added a new input xin(13) for the airflow fraction during offcycle (was PAR(25)). 
c                      This is the induced flow when the AC fan (RTFacf) is not ON.
c       HH  05/08/11 -- added logic for variable speed and two-speed AC.  If two speed parameter EER_rated_lo>0
c					and use two speed logic.  low --> Hi_STG_lo=0 or High --> Hi_STG_lo=1
c					If iac = 3 then use input compressor hz to change performance
c*******************************************************************************
      implicit none

C    REQUIRED BY THE MULTI-DLL VERSION OF TRNSYS
      !DEC$ATTRIBUTES DLLEXPORT :: TYPE140				!SET THE CORRECT TYPE NUMBER HERE
c
c       COMMON BLOCKS for  AC_HP, AC_HP_EF, DOE_AC

      common /HPBLK/ rown, hparea, ihp
      real*8 rown,hparea				  ! heat pipes: rows and area/side
      integer ihp                       ! heat pipe index

      common /Dswhlb/ dwarea,wdepth
      real*8 dwarea,wdepth              ! des whl: area/side and whl depth

      common /fan/ spmax,qmax,mtref
      real*8 spmax,qmax,mtref           ! fan: static, cfm, & motor efficiency

      common /messb/ imess
      integer imess

	common/doeacb/ eer_rated,shr_rated,Tadp
      real*8 EER_rated, SHR_rated       ! rated pefromance (w/o IDF) for DOE_AC
      real*8 Tadp                       ! ADP from DOE_AC, F

	common /doeac_coef/ ctc(10),cfc(3),etc(10),efc(3),coef_txt
	real*8 ctc,cfc,etc,efc			  !	DOE_AC Coeficient
	character*30 coef_txt			  ! text describing DOEAC coefs

c										Lennox Humiditrol Coefs
c									  ------------------------------------
	real*8  aLX1(4,10),aLX2(4,10),    ! coefs for EER correction (low, hi)
     &		bLX1(4,10),bLX2(4,10),    ! coefs for QT correction (low, hi)
     &		cLX1(6,10),cLX2(6,10),    ! coefs for SHR correction (low, hi)
     &		CR_LX1(10),CR_LX2(10),	  ! air flow adjustment ratio (low, hi)
     &		cfmt_LX1(10),cfmt_LX2(10) ! cfm/ton corresponding to low & hi
	character*60 LX_coef_txt(10)	  ! text describing each set of coefs
	integer nLX,iLX, iLX_sfan_exp
      real*8 ff,e1,e2,e3,e4,e5,e6,EER_lxfac,QT_lxfac,SHR_lxfac,CR_lxfac

      real*8 fshr                       ! FSHR() function
	real*8 Fplf						  ! Fplf() function	
      character*12 ftxt
	
c
c     define the standard TRNSYS variables:
	DOUBLE PRECISION xin(15)			!THE ARRAY FROM WHICH THE INPUTS TO THIS TYPE WILL BE RETRIEVED
	DOUBLE PRECISION out(12)				!THE ARRAY WHICH WILL BE USED TO STORE THE OUTPUTS FROM THIS TYPE
	DOUBLE PRECISION time				!THE CURRENT SIMULATION TIME - YOU MAY USE THIS VARIABLE BUT DO NOT SET IT!
	DOUBLE PRECISION par(35)			!THE ARRAY FROM WHICH THE PARAMETERS FOR THIS TYPE WILL BE RETRIEVED
	DOUBLE PRECISION t					!AN ARRAY CONTAINING THE RESULTS FROM THE DIFFERENTIAL EQUATION SOLVER
	DOUBLE PRECISION dtdt				!AN ARRAY CONTAINING THE DERIVATIVES TO BE PASSED TO THE DIFF.EQ. SOLVER

      integer      ISTAT,EMODE,iunits,icntrl
	integer*4    info(15)
c
c     Define PARAMETERS

c
      integer      imode                !Obsolete - always = 1
      integer      iac                  !AC unit type: 3= VSAC, 4=DOE_AC, 5=CWCOIL
      integer      ipflag,ipflag2       !print flag
      real*8       tons                 !nominal size of AC unit, tons
      real*8       dpsys                !system pressure drop, in H2O
      real*8       fnstef               !fan eff. (0-1)
      real*8       evapefc              !Evap cooler effect. on AC condenser

      real*8       rhkw                 !reheat kW
      real*8       frac                 !fraction of fan heat before HP or whl
      real*8       vcfm                 !ventilation cfm mixed at AC inlet (0) 
      REAL*8       bpfrc                !fraction of cfm to bypass evap. (0-1)
      real*8       gamma,tp,twet,anmax,tcl ! constants for FSHR function
      real*8       twet_o,gam_o,Mo,Ql_rated,qscw,qlcw,twet_cap
	real*8		 wcfm_ac			  ! A/C indoor fan watts per cfm
									  !   (= -1 if you'd rather use the
									  !    fan efficiency calcs) 
      integer      ishrf                ! select shr correlation 
	integer      nDOE_COF			  ! DOE_AC Coeficient number from file doe_ac.cof	
	integer		 idw				  ! type of CDQ desiccant wheel (1=GRI, 2=Kosar)

	real*8 NTUo,NTUo_nom
	real*8 toff_p,tp_p,NTUo_P,fspd_off,cfm_off1,fspd_off2,cfm_off2
	real*8 T_ON_c,T_OFF_c,pf,a1,a2,qevp,Ms,dt
      real*8 EER_rated_lo,SHR_rated_lo				! low speed ratings
	real*8 tons_frac_lo,Wcfm_ac_lo,tons_actual	! low speed factors / fractions
	real*8 none

c
c       Define INPUTS
c
      real*8       Tout                 !Outdoor temperature
      real*8       wout                 !Outdoor abs humidity
      real*8       mdot                 !mass flowrate for AC unit, lb/hr
      real*8       Tin                  !dry bulb temperature of incoming air
      real*8       Win                  !humidity ratio of incoming air
      integer      jbpON                ! Enable bypass control (=1)
									  ! Enable Lennox Humiditrol DH mode (=2) 
      real*8       rtf                  ! run time fraction for AC
	real*8       Hi_STG_c			  ! Indicates if high stage is activated high=1, low=0)
      real*8       fhz                  !AC compressor speed


c
c       Define OUTPUTS
c
      real*8       Qsens,Qlat           !Steady State delivered Btu/h
	real*8		 Qsens1, Qlat1	      !Actual delivered Btu/h 
c      real*8       ACkw                 !Actual AC power (kw)
c      real*8       Fankw                !Actual fan power (assuming CONST Fan)
c
c       Define Everything else
c
      real*8       cfm                  !cfm for AC unit
	integer      acType

c    

      real*8 edb,watts,tkw
      real*8 wbin,rhin,effhp,cfmo,totdp,Qto,shro
      real*8 scale,antu
      integer ihpcnd

	real*8    Tcwi,gpm,cw_area,cw_rows,gpm_o,Qcw_tot_o,SHR_cw
	real*8    tube_diam,tube_space,tube_space_ht,fpi
	real*8    rtf_err,rtf_err2,rtf_tol,relax
	Integer   cw_err_stat,Ntubes,Ncirc,rtf_cnt 

	integer Exp_Type, Etype
	real*8    c_eer(3,2), c_shr(3,2), c_cap(3,2)
	real*8    QT_cfac,EER_cfac,SHR_cfac,QT_tfac,EER_tfac,aa,tt,ww
	real*8	  Qtot_o,EER_o,SHR_o,ch_ratio	
	real*8    plf,clf,RTF_cor
	integer   i,j

c
c     define variables necessary for psych subroutine:
c

      integer      wbmode              !wet bulb mode flag to psych subroutine:
				       !     1--calculate Twb
				       !     0--don't calculate Twb
      integer      mode                !mode flag to psych subroutine:
				       !     1--Tdb and Twb input
				       !     2--Tdb and rh input
				       !     4--Tdb and W input
      double precision psydat(9)           !array of psychrometric data:
				       !     (1)--Patm (atm)
				       !     (2)--Tdb (F)
				       !     (3)--Twb (F)
				       !     (4)--relative humidity fraction
				       !     (5)--Tdp (F)
				       !     (6)--humidity ratio (lbm water/
				       !          lbm dry air
				       !     (7)--enthalpy (Btu/lbm dry air)
				       !     (8)--dens. of air-water mixture
				       !          (lbm/ft**3)
				       !     (9)--density of air in mixture
				       !          (lbm/ft**3)                         parameter    (iunits=2)          !unit flag to psych subroutine: 2=English
       parameter        (iunits=2)
c
C    SET THE VERSION INFORMATION FOR TRNSYS
      IF(INFO(7).EQ.-2) THEN
	  INFO(12)=16
	  RETURN 1
	ENDIF

C	LAST CALL MANIPULATIONS
	IF (INFO(8) .EQ. -1) THEN
		RETURN 1
	END IF

C	Post-Convergence Logic
	if (INFO(13) .GT. 0) THEN
		RETURN 1
	END IF

c     First Call Logic
      if (info(7) .eq. -1) then
		call typeck(1,info,15,35,0)    !check no. of inputs, parameters
		info(6) = 12                   !no of outputs   
		info(9) = 0                   !outputs depend only on inputs, not time
	    out(1:12)=0

c		--- read in coefficients for DOE_AC
		nDOE_COF  = int(par(31))				! no of desired coef set
		open(unit = 1001,file = "DOE_AC.COF")

		do j=1,nDOE_COF
		 read(1001,'(a30)') coef_txt
		 read(1001,'(10f)') (ctc(I),I=1,10)
		 read(1001,'(3f)') (cfc(I),I=1,3)
		 read(1001,'(10f)') (etc(I),I=1,10)
		 read(1001,'(3f)') (efc(I),I=1,3)
		end do
	    close(1001)

c			Read in Lennox Humiditrol Coefs

	  open(unit = 1002,file = "Lennox.COF")
        read(1002,'(i4)') nLx
	  read(1002,'(a60)') LX_coef_txt(10)  ! describes curve types
	  do j=1,nLX
		 read(1002,'(a60)') LX_coef_txt(j)
		 read(1002,'(4f)') (aLX1(I,j),I=1,4)
		 read(1002,'(4f)') (bLX1(I,j),I=1,4)
		 read(1002,'(6f)') (cLX1(I,j),I=1,6)
	     read(1002,'(2f)') cfmt_LX1(j), CR_LX1(j)
		 read(1002,'(4f)') (aLX2(I,j),I=1,4)
		 read(1002,'(4f)') (bLX2(I,j),I=1,4)
		 read(1002,'(6f)') (cLX2(I,j),I=1,6)
	     read(1002,'(2f)') cfmt_LX2(j), CR_LX2(j)
	  end do
	  read(1002,'(i)') iLX_sfan_exp
	  close(1002)

	  open(unit = 1001,file = "PERF_COF_140.dat")
	     write(1001,'(20("*"),a,20("*"))') 
     &	  '  CURVES USED FOR DOE_AC in TYPE140  '
		 write(1001,'(a30)') coef_txt
		 write(1001,'(10f)') (ctc(I),I=1,10)
		 write(1001,'(3f)') (cfc(I),I=1,3)
		 write(1001,'(10f)') (etc(I),I=1,10)
		 write(1001,'(3f)') (efc(I),I=1,3)
	     write(1001,'(20("*"),a,20("*"))') 
  
	     write(1001,'(20("*"),a,20("*"))') 
     &	  '  CURVES AVAILABLE FOR LENNOX HUMIDITROL in TYPE140  '
	  do j=1,nLX
	     write(1001,'(a,i)') 'COEFs for DH mode = ',j
		 write(1001,'(a60)') LX_coef_txt(j)
		 write(1001,'(4f)') (aLX1(I,j),I=1,4)
		 write(1001,'(4f)') (bLX1(I,j),I=1,4)
		 write(1001,'(6f)') (cLX1(I,j),I=1,6)
	     write(1001,'(2f)') cfmt_LX1(j), CR_LX1(j)
		 write(1001,'(4f)') (aLX2(I,j),I=1,4)
		 write(1001,'(4f)') (bLX2(I,j),I=1,4)
		 write(1001,'(6f)') (cLX2(I,j),I=1,6)
	     write(1001,'(2f)') cfmt_LX2(j), CR_LX2(j)
	  end do
	  write(1001,'(i)') iLX_sfan_exp
	  close(1001)
      endif
c
c     read parameters (constants)
c

      imode = int(par(1)+.5)
	iac = int(par(2)+.5)
      tons = DBLE(par(3))
      dpsys = DBLE(par(4))
      fnstef = -DBLE(par(5))    !make fnstef < 0 so FC_MAX won't be called
      ipflag = int(abs(par(6))+.5)
	if (Par(6) .lt. 0) then       !if IPFLAG<0 then print for only 200 hours
	  ipflag2 = ipflag + 200
	else
	  ipflag2 = 8761.
	endif
      rown = DBLE(par(7))
      hparea = DBLE(par(8))
	if (hparea .lt. 0) hparea=tons     ! autosize with tonnage
      dwarea = hparea
      ihp = max(int(par(9)+.5),0)  ! if>0 use as Heat Pipe index
      idw = max(int((-par(9))+.5),0)  ! if<0 use as des whl index (1 or 2)
c      wdepth = DBLE(par(10))
	wdepth = rown			 ! wheel depth = row #
      mtref = DBLE(par(11))
      evapefc = DBLE(par(12))
c				   par(13) is not used	
      rhkw = DBLE(par(14))
      frac = DBLE(par(15))
      SHR_rated = DBLE(par(16))
      EER_rated = DBLE(par(17))
      bpfrc = DBLE(par(18))
      ishrf = int(par(19))
      twet_o = DBLE(par(20))
      gam_o = DBLE(par(21))
      ANMAX = DBLE(abs(par(22)))
      TCL = DBLE(par(23))
	NTUo_nom = DBLE(par(24))
c	fspd_off2 = DBLE(par(25)) !flow/speed fraction for 2nd off period   NOW AN INPUT
c      par(26) & par(27) are not used
	wcfm_ac = DBLE(par(28))
	ch_ratio = DBLE(par(29))
	Exp_Type = int(par(30)) !(1-Orifice 2- TXV)
c     nDOE_COF  is par(31), see above	

      EER_rated_lo  = DBLE(par(32))		! low stage parameters (for 2-speed unit)
      SHR_rated_lo  = DBLE(par(33))
      tons_frac_lo  = DBLE(par(34))
      wcfm_ac_lo    = DBLE(par(35))
	
c
	IF (ipflag .gt. 100) THEN               ! ipflag is a time trip
	   IF (INT(time) .ge. ipflag .and. INT(time) .lt. ipflag2) THEN
		ipflag = 13
	   ELSE
		ipflag = 0
	   END IF
	END IF

	IF (ipflag .gt. 0) then
	  imess = 1            ! turn on output
	  write(ftxt,'(i2.2)') ipflag
	  open(unit=ipflag,file='FOR0'//ftxt//'.dat')
	  write(ipflag,*) 'Time: ',time
	  write(ipflag,*) 'xin: ',xin
	  write(ipflag,*) 'Out: ',out
	  write(ipflag,*) 't: ',t
	  write(ipflag,*) 'dtdt: ',dtdt
	  write(ipflag,*) 'par: ',par
	  write(ipflag,*) 'info: ',info
	  write(ipflag,*) 'icntrl: ',icntrl 
	ENDIF

c
c     
c  read inputs (variables)
c
      Tin = (xin(1))
      Win = (xin(2))
      Tout =(xin(3))
      wout =(xin(4))
      mdot =(xin(5))
      jbpON=(xin(6))

	rtf = (xin(7))				! RTF_SHR (used for LHR degradation)
	clf = (xin(8))				! RTFc (used to find PLF)
	toff_p = xin(9)				! length of 1st offcycle period (minutes)
	fspd_off = xin(10)			! airflow ratio during off cycle 

c								  *** Used for SHORT TIME STEP Model ****** 
	T_ON_c  = xin(11)			! Cooling ON time (hrs) (equals zero if OFF)
	T_OFF_c = xin(12)			! Cooling OFF time (hrs) (equals zero if ON)
      fspd_off2 
     &    = max(fspd_off2,xin(13))! the off-cycle INDUCE airflow fraction is now an INPUT HH 10/31/10


	Hi_STG_c = xin(14)			! High Stage flag (used for two stage units - May 2011)

	fhz       = xin(15)			! compressor variable speed signal (0-1) 


	tons_actual = tons				! tons = nominal unit size (high for a two stage),  
									! tons_actual = nominal size of active stage (low or high)

c	----------------------- Two-speed logic

	If (EER_rated_lo .gt. 0.1 .and. iac .eq. 4) then
        if (Hi_STG_c .eq. 0) then		! Override for low speed (=0)
		EER_rated = EER_rated_lo
	    SHR_rated = SHR_rated_lo
	    tons_actual = tons * tons_frac_lo   !actual unit size

c	    The airflow (mdot or input(5) ) must be adjusted before being INPUT into this routine
		wcfm_ac = wcfm_ac_lo 
	  endif
	endif

c	----------------------- Variable-speed logic

	If (EER_rated_lo .gt. 0.1 .and. iac .eq. 3) then
	    fhz = max ( min(fhz,1.), 0.)
		EER_rated = EER_rated*fhz + EER_rated_lo*(1-fhz)
		SHR_rated = SHR_rated*fhz + SHR_rated_lo*(1-fhz)
		tons_actual =    tons*(fhz + tons_frac_lo*(1-fhz))

c	    The airflow (mdot or input(5) ) must be adjusted before being INPUT into this routine
		wcfm_ac = wcfm_ac*fhz + wcfm_ac_lo*(1.-fhz) 
	endif
c	------------------------- add/remove coil moisture if TIME advances
	if (TIME .ne. OUT(11)) then  
	  dt = TIME - OUT(11)		 ! timestep
	  out(12) = max(min(out(12) + out(6)*dt/1060.,Mo), 0.0)   ! out(6) is Qlat
	endif
	Ms = out(12)				! set Ms = moisture at end of last timestep

c
c      
c       Initialize outputs
c
	Qsens=0.
	Qlat=0.
	tkw=0.
	watts=0.
	rtf_cnt = 0
	rtf_tol = 0.02
	relax =2.		! step twice as big as tolleranc
	rtf_err2=0.
	CR_lxfac  = 1.
c

       
	IF (mdot .eq. 0. .or. Tin .lt. 35 .or. Win .eq. 0) GOTO 500              ! exit if no flow
c


c     call psych to get complete information on incoming air:
      psydat(1) = 1
      psydat(2) = SNGL(Tin)
      psydat(6) = SNGL(Win)
      mode = 4
      wbmode = 1
	
      CALL PSYCHROMETRICS(TIME,INFO,IUNITS,MODE,WBMODE,PSYDAT,EMODE,
     1	ISTAT)
	Win = psydat(6)    !  this is a fix in case the incoming
				       !  humidity is physically impossible--
				       !  at least one of the weather files
				       !  has mistakes
      wbin = psydat(3)
      rhin = psydat(4)*100.   ! as percentage

	edb = 60.0
	vcfm=0.

	cfm = mdot/(0.075*60.)  ! find cfm at standard air (for AC_xx_EF)

c
	if (ipflag .gt. 0) write(ipflag,*) 'jbpON=',jbpon

	IF (jbpON .eq. 1) cfm = cfm*(1.-bpfrc)  !Bypass option

	Ql_rated = tons_actual*12000.*(1.-SHR_rated)    ! Btuh    
	
c	write(ipflag,*) imode,iac
	IF (imode .eq. 1 .and. iac .le. 4) THEN 
	
	  If (idw .gt. 0) THEN 
           effhp = float(-idw)							! CDQ des wheel
	     cfmo=cfm
	  ELSE
	     call ac_hp_ef (iac,tons_actual,edb,cfm,dpsys,fnstef,  ! heat pipe
     +                 ipflag,effhp,watts,cfmo,totdp)
	  ENDIF
c
	  IF (wcfm_ac .ge. 0.)then	! override ac_hp_ef's calculation
	     watts=cfm*wcfm_ac			! of 'watts', using w/cfm input value
	  ENDIF

	  IF (jbpON .eq. 1) THEN
		watts = watts/(1.-bpfrc)        ! base fan watts on
c                                               ! total cfm
c          ELSE
c          **DISABLED**  effhp = 0.             ! overide heat pipes if
c                                               ! humidity control NOT NEEDED
	  END IF
c
 
	  call ac_hp (iac,none,tons_actual,frac,effhp,evapefc,watts,Tin,wbin,
     &              Tout,wout,cfmo,rhkw,ipflag,vcfm,Qsens,Qlat,tkw,
     &              ihpcnd)

c
c
c	  Apply Charge Ratio Correction to AC for Capacity, EER & SHR
c	  Coefficeints for Orifice (1st row, Exp_type=1) & TXV (2nd row,EXP_type=2)
c       Also apply correction

	  data c_eer /-1.3744450, 4.5664984, -2.1987032,
     &	0.051466055, 1.9260348, -0.97870189/
	  data c_cap /-1.7810837, 5.1948408,	-2.4247714,
     &	0.082344576, 1.7502776, -0.83302159/
	  data c_shr /0.55515179, 0.61807582, -0.17174450,
     &	        1.0,	0.0,	0.0/
        if (ch_ratio .eq. 1.) then
	    EER_cfac = 1.0
	    QT_cfac  = 1.0
	    SHR_cfac = 1.0
        else
	    Etype = abs(Exp_Type)						! use either 1 or -1 as "orifice"
	    EER_cfac = (c_eer(1,Etype)+c_eer(2,Etype)*
     &			ch_ratio+c_eer(3,Etype)*ch_ratio**2)
	    QT_cfac  = (c_cap(1,Etype)+c_cap(2,Etype)*
     &			ch_ratio+c_cap(3,Etype)*ch_ratio**2)
	    SHR_cfac = (c_shr(1,Etype)+c_shr(2,Etype)*
     &			ch_ratio+c_shr(3,Etype)*ch_ratio**2)
        endif
        if (Exp_Type .eq. 1) then !Orifice Performance map correction
          tt = max(min(Tout,115.),82.)	! range of correction data
	    aa = (637.10691 - 21.071441 * tt
     1		            + 0.22816566*tt**2 - 0.00081004820*tt**3)
	    EER_tfac = 1. + aa/100.
	    aa = (393.56217-13.790335*tt+0.15604904*tt**2
     1				    -0.00057317143*tt**3)
	    QT_tfac = 1. + aa/100.
	  else
	    EER_tfac=1.0			  ! No correction for TXV
	    QT_tfac=1.0
	  endif

	  if (jbpON .ge. 2) then    !Lennox Humiditrol unit

          iLX = jbpON-1			!jbpON=2 for DH mode, =3 for Enhanced DH mode 
		ff=min(max((cfmo/tons_actual-cfmt_LX1(iLX))/
     &				(cfmt_LX2(iLX)-cfmt_LX1(iLX)),-0.2),1.2)

          tt = max(min(Tout,95.),60.)	! range Tout data for Humiditrol
          ww = max(min(wbin,70.),60.)	! range wbin data for Humiditrol

		e1 = aLX1(1,iLX) + aLX1(2,iLX)*tt + aLX1(3,iLX)*ww 
     &				 + aLX1(4,iLX)*tt*ww
		e2 = aLX2(1,iLX) + aLX2(2,iLX)*tt + aLX2(3,iLX)*ww 
     &				 + aLX2(4,iLX)*tt*ww
		EER_lxfac = e1 + (e2-e1)*ff

		e3 = bLX1(1,iLX) + bLX1(2,iLX)*tt + bLX1(3,iLX)*ww 
     &				 + bLX1(4,iLX)*tt*ww
		e4 = bLX2(1,iLX) + bLX2(2,iLX)*tt + bLX2(3,iLX)*ww 
     &				 + bLX2(4,iLX)*tt*ww
		QT_lxfac = e3 + (e4-e3)*ff

		e5 = cLX1(1,iLX) + cLX1(2,iLX)*tt + cLX1(3,iLX)*rhin 
     &		+ cLX1(4,iLX)*tt*rhin 
     &		+ cLX1(5,iLX)*tt**2 + cLX1(6,iLX)*rhin**2 
		e6 = cLX2(1,iLX) + cLX2(2,iLX)*tt + cLX2(3,iLX)*rhin 
     &       + cLX2(4,iLX)*tt*rhin 
     &	   + cLX2(5,iLX)*tt**2 + cLX2(6,iLX)*rhin**2 
		SHR_lxfac = e5 + (e6-e5)*ff

		CR_lxfac = CR_LX1(ilx) + (CR_LX2(iLX)-CR_LX1(iLX))*ff
        else
		EER_lxfac = 1.0
		QT_lxfac = 1.0
		SHR_lxfac = 1.0
		CR_lxfac = 1.0
	  endif

	  watts = watts*(CR_lxfac)**iLX_sfan_exp   ! adjust Supply fan power for Lennox Humiditrol case
        
        Qtot_o= (Qsens + Qlat)*QT_cfac*QT_tfac*QT_lxfac
        EER_o = ((Qsens + Qlat)/tkw)*EER_cfac*EER_tfac*EER_lxfac
        SHR_o = min((Qsens/(Qsens + Qlat))*SHR_cfac*SHR_lxfac,1.0)

	  Qsens = Qtot_o*SHR_o
	  Qlat = Qtot_o - Qsens
	  tkw = Qtot_o/EER_o

	  IF (ihpcnd .eq. 1) then
	     write(55,*) 'condensation on heat pipe in AC_HP'
		 write(55,*)'Tin = ',tin
		 write(55,*)'Win = ',win    
		 write(55,*)'Tout =',tout   
		 write(55,*)'wout =',wout   
		 write(55,*)'mdot =',mdot  
		 write(55,*)'jbpON=',jbpon  
           write(55,*)'rtf = ',rtf        
           write(55,*)'iac =',iac
           write(55,*)'fhz =',fhz
           write(55,*)'tons =',tons
           write(55,*)'frac =',frac
           write(55,*)'effhp =',effhp
           write(55,*)'evapefc =',evapefc
           write(55,*)'watts =',watts
           write(55,*)'wbin =',wbin
           write(55,*)'cfmo =',cfmo
           write(55,*)'rhkw =',rhkw
           write(55,*)'ipflag =',ipflag
           write(55,*)'vcfm =',vcfm
           write(55,*)'qsens =',qsens
           write(55,*)'qlat =',qlat
           write(55,*)'tkw =',tkw
           write(55,*)'ihpcnd =',ihpcnd
c	     stop
	  endif
	END IF  ! ------------------------------- End DX Coil (iac=4) ----------------
c
c----------------------------- CW COIL (iac=5) -----------------------------------------
c		Partload CW model assumes that gpm is linearly proportional to total capacity 
c		and actual gpm is a function of RTF
c		SHR of coil at part load is used to adjust full load cw coil capacity
c         HH Jan 26, 2005  

	IF (imode .eq. 1 .and. iac .eq. 5) THEN  

c	  coil for terry brennan, Hilton hotel room
        cw_area = tons 			! coil area
	  tube_diam  = 0.5			! in
	  tube_space = 1.			! in between rows
	  tube_space_ht = 1.		! in within row
	  Ntubes = int(gam_o)		! number of tubes in the face row
	  Ncirc = Ntubes/2          ! No of face tubes in each circuit(can be 1,2,4)
	  Tcwi = EER_rated  		! chilled water temp
	  gpm_o = SHR_rated			! CW flow 
        cw_rows = DBLE(ishrf)		! rows			
	  fpi = twet_o				! fin spacing
        
    	  call cwcoil_eng (Tin,win,Tcwi,abs(gpm_o),cfm,cw_area,cw_rows,
     &         tube_diam,tube_space,tube_space_ht,fpi,Ntubes,Ncirc,
     &		 ipflag,Qsens,Qlat,cw_err_stat)
	  Qcw_tot_o = Qsens + Qlat
	  IF (cw_err_stat .eq. 1) 
     &    write(*,*) '**WARNING CWCOIL Err-GPM0 *** ',
     &       time,Qsens,Qlat,gpm_o
	  watts=cfm*wcfm_ac
	  tkw = watts/1000. + gpm_o
	  Tadp = cw_err_stat

        if (gpm_o .lt. 0.) goto 250			! if gpm_o<0 then use full flow 
										! assume CHW valve cycles
	  gpm = gpm_o*RTF  
200	  if (gpm .gt. 0.1) then
    	      call cwcoil_eng (Tin,win,Tcwi,gpm,cfm,cw_area,cw_rows,
     &         tube_diam,tube_space,tube_space_ht,fpi,Ntubes,Ncirc,
     &		 ipflag,Qsens,Qlat,cw_err_stat)
	      IF (cw_err_stat .eq. 1) 
     &          write(*,*) '**WARNING CW COIL Err-GPM ***',time,
     &		  Qsens,Qlat,gpm
            SHR_cw = Qsens/(Qsens+Qlat+1.d-25)
	  ELSE
            SHR_cw = 1.
	      Qsens = Qcw_tot_o*RTF
	      Qlat=0.
	  ENDIF
	  if (rtf_cnt .ge. 5) write(*,*) 'gpm,tin,win,',
     &	'Qsens,Qlat=',gpm,tin,win,Qsens,Qlat,cw_err_stat,rtf_err,RTF

        rtf_err2 = rtf_err
	  rtf_err = RTF - (Qsens+Qlat)/Qcw_tot_o
	  IF (rtf_err .gt.  rtf_tol) gpm = gpm + gpm_o*rtf_tol*relax
	  IF (rtf_err .lt. -rtf_tol) gpm = gpm - gpm_o*rtf_tol*relax
	  if (sign(1._8,rtf_err) .ne. sign(1._8,rtf_err2))
     &										relax = relax*0.5 
	  rtf_cnt = rtf_cnt + 1

	  if (abs(rtf_err) .gt. rtf_tol .and. rtf_cnt .le. 20 .and.
     &		RTF .gt. 0) goto 200

        if (abs(rtf_err) .gt. rtf_tol .and. rtf_cnt .gt. 1) 
     &     write(*,*) '%%%%%%%%%%%%% ',
     &     'GPM RTF DID NOT Converge: ',TIME,rtf_cnt,RTF,
     &     rtf_err,rtf_err2,Qsens,Qlat,gpm,gpm_o*RTF
	  Qsens = MAX(Qcw_tot_o*SHR_cw,0d0)
	  Qlat = MAX(Qcw_tot_o - Qsens,0d0)
	  Tadp = cw_err_stat
	  tkw = watts/1000. + gpm
	END IF !------------------------- End CW COIL (iac=5) -------------------
c
250	Qsens=Qsens*1000. + watts*3.412
	Qlat=Qlat*1000.
	Qsens1 = Qsens
	Qlat1 = Qlat
c
	if (iac .eq. 5) goto 500     ! part load SHR not needed/allowed for CW coil

	if (par(22) .gt. 0.) then	 ! if Nmax > 0
	    plf = Fplf(clf,tcl,anmax) !part load correction
	else
		plf = 1.
	endif

	If (T_ON_c .gt. 0.) then
	    pf = 1.0-exp(-T_ON_c*3600./TCL)	! apply time constant (TCL, sec) at startup to sensible and latent
	    Qsens1 = Qsens*pf
	    Qlat1 = Qlat*pf
	    plf=1.0
	endif
	
	IF (ishrf .ge. 1 ) THEN       ! Orignal Model (linear decay)
	  twet_cap = 9999.
	  Mo = twet_o*Ql_rated/(1060.*3600.)    ! lbs

	  twet = DMIN1(Mo*3600.*1060./(Qlat+1.0d-25), twet_cap)  ! cap twet
								 ! HH 3/30/95

	  if (ishrf .eq. 1) then  !12/21/05
		  gamma = DMIN1(gam_o*Ql_rated*(Tin-wbin)/
     1		                               (13.*Qlat+1.0d-25),100.d0)  ! 1/24/05
	  endif
	  if (ishrf .ge. 2 .and. ishrf .le. 4) then	 ! New Model & simple delays
		   tp = Mo*1060/(1.08*cfm*(Tin-wbin))*3600
		   NTUo = NTUo_nom * (450 * TONS)**0.2/(cfm)**0.2
	  endif

	  if (ishrf .eq. 5) then
	       cfm_off2 = fspd_off2*cfm			!assume small % of full flow
		   tp = Mo*1060/(1.08*cfm_off2*(Tin-wbin))*3600    
		   NTUo = NTUo_nom * (450 * TONS)**0.2/(cfm_off2)**0.2

	       cfm_off1 = fspd_off*cfm      !use flow fraction
		   tp_p = Mo*1060/(1.08*cfm_off1*(Tin-wbin))*3600    
		   NTUo_p = NTUo_nom * (450 * TONS)**0.2/(cfm_off1)**0.2
	  endif 
	  
	  If (T_OFF_c .gt. 0.) then			! ----------------- Transient SHORT TIME STEP off-cycle evap models
	    IF (rtf .eq. 1) then
		  cfm_off1 = fspd_off*cfm			!use specified % of full flow when rtfacf=ON
	    else
		  cfm_off1 = fspd_off2*cfm			!assume very small % of full flow when rtfacf=OFF
      	endif
		tp = Mo*1060/(1.08*cfm_off1*(Tin-wbin))*3600    
		NTUo = NTUo_nom * (450 * TONS)**0.2/(cfm_off1)**0.2
		a1 =  exp(-NTUo*dt*3600./tp)		! use tstep instead of time (since Ms is updated each tstep)
		a2 =  exp(NTUo*Ms/Mo) - 1.
		qevp = (Ql_rated*twet_o/tp)*(a1*a2)/(a1*a2+1)	! changed twet --> twet_o   May-30-2011
		Qsens1 = qevp
		Qlat1  = -qevp
		PLF = 1.

	  else								! ----------------- ORIGINAL Steady-state partload models
	    Qto = Qsens1 + Qlat1
	    shro = Qsens1/(Qto+1.0d-25)

	    RTF_cor = rtf/plf
	    Qsens1 = Qto*FSHR(ishrf,shro
     1       ,gamma,tp,twet,anmax,tcl,RTF_cor,NTUo,toff_p,tp_p,NTUo_P)
	    Qlat1 = Qto - Qsens1
	  endif
	END IF


500   out(1) = (Tin)                        ! inlet to AC
      out(2) = (win)

	IF (T_ON_c+T_OFF_c .gt. 0) then					! only used w/ SHORT TIMESTEP model
	  IF (clf .eq. 1.) then
	     out(3) = cfm*CR_lxfac*(0.075*60.)			! airflow witn AC is ON (after adjustments)
        else
          out(3) = cfm_off1*(0.075*60.)               ! Offcycle mass flow rate (lb/hr)
	  endif 
	else
	  out(3) = mdot
	endif

	IF (imode .eq. 1 .and. iac .eq. 5) THEN 
		out(4) = (tkw-watts/1000.)            ! cooling coil mode outputs GPM in out(4)
	else
		out(4) = (tkw-watts/1000.)/plf        ! total power w/o IDF (kW)
	endif

      out(5) = (Qsens1)                      ! AC GROSS sensible (Btu/h)
      out(6) = (Qlat1)                       ! AC latent (Btu/h)
      out(7) = (watts/1000.)                ! Indoor Fan kW 
      out(8) = (Tadp)                       ! ADP of AC unit
	out(9) = PLF
	out(10)= CR_lxfac					  ! factor to adjust inlet supply airflow (for Lennox unit)
	
	out(11) = time						! keep track of time
c     out(12) is moisture on coil (at the end of the last timestep) see above                   	

      if (ipflag .gt. 0) then
        write(124,501) info(7),out(1:12),T_ON_C,T_OFF_c,Mo,
     &		NTUo_nom,NTUo,tp,twet,Ql_rated,Qlat
501     format(i4,15f11.4,6g11.4)                    
	endif

      return 1
      end
