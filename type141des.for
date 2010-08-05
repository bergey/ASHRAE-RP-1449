      Subroutine type141 (time,xin,out,t,dtdt,par,info,icntrl,*)
c*******************************************************************************
C
C       This routine calls Specific Desiccant Routines 
c         
c     INPUTS:     <1> Tpin -   Process Inlet Temperature (F)
c                 <2> wpin -   Process Inlet Humidity (lb/lb)
c                 <3> mdot -   Process Air Flow rate (lb/h)
c                 <4> Trin -   Regeneration Inlet Temperature (F)
c                 <5> wrin -   Regeneration Inlet Humidity (lb/lb)       
c
c     PARAMETERS: <1> isys -  System type (0=none,  1=Albers, 2=ICC,
c                                          3=silica gel,4=type-1M,5=Enth Whl,
c                                          6=ICC_ELE,7=Addison 100% Fresh Air,
c					   8=Kathabar XXX?, 9=Munters Unit, 10=Drykor UDT 7.5, 
c					   11=Residential DH, 12=Residential Desiccant,
c					   13=Semco, 14=MAU, 15=Munters HCU)
c				<2> ipflag  - print variable
c
c      System-specific   0      1       2      3       4        5      
c         Parameters:   None  Albers  ICC   Silica  Type-1M  Enth Whl
c					  ****  ******  ***   ******  *******  ********
c                 <3>   W_cfm na      na    W_cfm   W_cfm    eff
c                 <4>                                        W_cfm
c                 <5>										   W_cfm2
c                     ------------------------------------------------
c                        6      7       8      9       10	
c                     ICC_ele Addis   Kath  Munters  Drykor
c					******* *****   ****  ******** ******
c                 <3>   na    na      ktons tons_rat  no_of_units
c                 <4>   W_cfm               Wcfm_p    W_cfm
c                 <5>                       Wcfm_r    W_cfm2
c                 <6>                       shx_eff
c                 <7>                       evp_eff
c                 <8>                       pc_cntl (Post Cooling Set Pt) 
c				<9>						  shx_leak
c				<10>					  wtype
c				<11>					  eer_rat
c				<12>					  shr_rat
c                     ------------------------------------------------
c                        11		12
c                       resdh		desdh	
c					  *****     *****
c                 <3>   cfm_nom	cfm_nom
c                 <4>   W_cfm		W_cfm
c                 <5>             W_cfm_unit (overrides ELEC from desdh)
c                 <6>   
c                 <7>   
c                 <8>   
c				<9>	
c				<10>  dhtype    dhtype
c				<11>
c				<12>
c
c                        13			14					15
c                       Semco			Makeup Air unit		Munters HCU
c					  *****			***************		***********		
c                 <3>   tons_rat_pc	tons_rate_mau		iwtype
c                 <4>   Wcfm_p		Wcfm_p				Wcfm_p
c                 <5>   Wcfm_r		ishrf				no_of_units
c                 <6>   an_units		twet_o				T_on_stg1
c                 <7>   f_byp			gam_o				T_on_stg2
c                 <8>   pc_cntl		rht_cntl
c				<9>	  Tris			TCL_min
c				<10>  iwtype		n_stg
c				<11>  EER_rat_pc	EER_rat_mau
c				<12>  SHR_rat_pc	SHR_rat_mau
c				<13>  wrset_spt1    tcl
c				<14>  wrset_spt2	ANMAX
c				<15>  tas_delta		NTUo_nom
c				<16>  trset_spt1	toff_p
c				<17>  trset_spt2	tp_p
c				<18>  reset_var		NTUo_P
c
c	OUTPUTS:	<1> Tpo -					Leaving air temp (F)  - includes fan heat
c				<2> wpo -					Leaving air humidity (lb/lb)
c				(3) (tkw-wattp/1000.) -		total power w/o Proc.Fan (kW)
c				(4) (Qs*1000.) -			net sensible (Btu/h) - includes fan heat
c				(5) (Ql*1000.) -			net latent  (Btu/h)
c				(6) (wattp/1000.) -			Process Fan Power (kW)
c				(7) (Gas) -					Gas input (kBtu/h) 
c
c	VARIABLE LIST:
c
c       HH <01/04/96>  new version calls Kathabar, Albers, ICC, Silica, & Type-1M
c       MC <03/25/97>  added ICC_ELE from EDES project
c       MC <04/01/97>  added Addison for  EDES project
c       DC <03/20/02>  added drykor & Munters
c	  ST <04/14/03>  added residential DH
c	  ST <07/27/04>	 added Cinemark IADR Option
c	  HH <04/04>     added MAU with staging, reheat & HGB
c	  HH <05/27/05>  added Munters HCU unit
c       HH <01/17/07>  resDH & desDH coefs now come from a *.COF files
c*******************************************************************************
      implicit none

C    REQUIRED BY THE MULTI-DLL VERSION OF TRNSYS
      !DEC$ATTRIBUTES DLLEXPORT :: TYPE141				!SET THE CORRECT TYPE NUMBER HERE
c
c
c     define the standard TRNSYS variables: 
	DOUBLE PRECISION XIN(6)				!THE ARRAY FROM WHICH THE INPUTS TO THIS TYPE WILL BE RETRIEVED
	DOUBLE PRECISION OUT(7)				!THE ARRAY WHICH WILL BE USED TO STORE THE OUTPUTS FROM THIS TYPE
	DOUBLE PRECISION TIME				!THE CURRENT SIMULATION TIME - YOU MAY USE THIS VARIABLE BUT DO NOT SET IT!
	DOUBLE PRECISION PAR(18)			!THE ARRAY FROM WHICH THE PARAMETERS FOR THIS TYPE WILL BE RETRIEVED
	DOUBLE PRECISION T					!AN ARRAY CONTAINING THE RESULTS FROM THE DIFFERENTIAL EQUATION SOLVER
	DOUBLE PRECISION DTDT(1)			!AN ARRAY CONTAINING THE DERIVATIVES TO BE PASSED TO THE DIFF.EQ. SOLVER
      INTEGER*4 INFO(15)					!THE INFO ARRAY STORES AND PASSES VALUABLE INFORMATION TO AND FROM THIS TYPE
	INTEGER*4 ICNTRL					!AN ARRAY FOR HOLDING VALUES OF CONTROL FUNCTIONS WITH THE NEW SOLVER

	integer      ISTAT,EMODE,i,j
      DOUBLE PRECISION psydat(9)
	INTEGER      WBMODE,MODE,IUNITS
c
c      
      COMMON /kathb/ gas_max,ehx,ebrnr
      REAL*8	gas_max,ehx,ebrnr,Tpwb
      COMMON /deswhlb/ warea, gasef, Tri, pfanef, rfanef,mtrefc
      real*8 warea, gasef, Tri, pfanef, rfanef,mtrefc
      COMMON /evapb/ evapefp,evapefr
	real*8 evapefp,evapefr
	common /doeac_coef/ ctc(10),cfc(3),etc(10),efc(3),coef_txt
	real*8 ctc,cfc,etc,efc			  !	DOE_AC Coeficient
	character*30 coef_txt			  ! text describing DOEAC coefs
	integer nDOE_COF

	common /RDH_coef/ A1(4,10),B1(4,10),C1(4,10),
     &                  t_rng1(2,10),rh_rng1(2,10)
	real*8 A1,B1,C1,t_rng1,rh_rng1								!	ResDH Coeficients
      common /DDH_coef/ A2(4,10),B2(4,10),C2(4,10),D2(4,10),
     &                  t_rng2(2,10),rh_rng2(2,10)
	real*8 A2,B2,C2,D2,t_rng2,rh_rng2							!	DesDH Coeficients

	character*60 ResDHcoef_txt(10),DesDHcoef_txt(10)	! text describing coefs
	integer nResDH, nDesDH

      REAL*8 Tpin,wpin,scfm,Trin,wrin,mdot,dpth,vcfm,qln
      REAL*8 fanef,mtref,ktons,heff,aqs,aql,akw
      INTEGER isys,ipflag,isiz,ized,iwtype, dhtype
      REAL*8 Qs,Ql,Tpo,wpo,zed,aone,w_cfm,eff,W_cfm2
      REAL*8 gas,tkw,wattp,pkw,rkw,wkw,dpr,dpp,rcfm,tria,afrac
	REAL*8 evp_eff,pc_cntl,tco_limit,wrset_spt1,wrset_spt2
	REAL*8 tas_delta, trset_spt1,trset_spt2,reset_var
	REAL*8 no_of_units,scfm0,QT0,SHR,COP,QT ,kw_t
	REAL*8 eer_rat_pc,shr_rat_pc,tons_rat_pc,wdiam,wfrac
	REAL*8 shx_eff,shx_leak,wreac,scfmo,tpi,wpi,wcfm_p,wcfm_r 
	REAL*8 qreac,kw_sfan,cfm_nom,HA,CAP,ELEC   
	REAL*8 f_prg,f_byp,Tris,brnr_eff,an_units 
	REAL*8 eer_rat_mau,shr_rat_mau,tons_rat_mau,TCL_min,rht_cntl
	integer n_stg,istg
	REAl*8 T_on_stg1,T_on_stg2

	
	REAL*8 ishrf,RTFd,twet,gam_o,ANMAX,tcl,NTUo,NTUo_nom
	REAL*8 toff_p,tp_p,NTUo_P
	REAL*8 acType,Qtot,shro,tp,gamma,FSHR
	REAL*8 twet_cap,Mo,Ql_rated,twet_o

c
c     if this is the first call to this unit, do the usual TRNSYS stuff:
	
C    SET THE VERSION INFORMATION FOR TRNSYS
      IF(INFO(7).EQ.-2) THEN
	  INFO(12)=16
	  RETURN 1
	ENDIF

      if (info(7) .eq. -1) then
      call typeck(1,info,6,18,0)       !check no. of inputs, parameters
        info(6) = 7                    !no of outputs   
        info(9) = 0                    !outputs depend only on inputs, not time

c		--- read in coefficients for DOE_AC
	  nDOE_COF  = 1							! for MAU only use 1st coef set
	  open(unit = 1001,file = "DOE_AC.COF")

	  do j=1,nDOE_COF
		 read(1001,'(a30)') coef_txt
		 read(1001,'(10f)') (ctc(I),I=1,10)
		 read(1001,'(3f)') (cfc(I),I=1,3)
		 read(1001,'(10f)') (etc(I),I=1,10)
		 read(1001,'(3f)') (efc(I),I=1,3)
	  end do
	  close(1001)

	  open(unit = 1002,file = "ResDH.COF")
        read(1002,'(i4)') nResDH
	  read(1002,'(a60)') ResDHcoef_txt(10)  ! describes curve types
	  do j=1,nResDH
		 read(1002,'(a60)') ResDHcoef_txt(j)
		 read(1002,'(4f)') (A1(I,j),I=1,4)
		 read(1002,'(4f)') (B1(I,j),I=1,4)
		 read(1002,'(4f)') (C1(I,j),I=1,4)
		 read(1002,'(4f)') (t_rng1(I,j),I=1,2),(rh_rng1(I,j),I=1,2)
	  end do
	  close(1002)


	  open(unit = 1003,file = "DesDH.COF")
        read(1003,'(i4)') nDesDH
	  read(1003,'(a60)') DesDHcoef_txt(10)  ! describes curve types
	  do j=1,nDesDH
		 read(1003,'(a60)') DesDHcoef_txt(j)
		 read(1003,'(4f)') (A2(I,j),I=1,4)
		 read(1003,'(4f)') (B2(I,j),I=1,4)
		 read(1003,'(4f)') (C2(I,j),I=1,4)
		 read(1003,'(4f)') (D2(I,j),I=1,4)
		 read(1003,'(4f)') (t_rng2(I,j),I=1,2),(rh_rng2(I,j),I=1,2)
	  end do
	  close(1003)

	  open(unit = 1001,file = "PERF_COF_141.dat")
	     write(1001,'(20("*"),a,20("*"))') 
     &	  '  CURVES USED FOR DOE_AC in TYPE141  '
		 write(1001,'(a30)') coef_txt
		 write(1001,'(10f)') (ctc(I),I=1,10)
		 write(1001,'(3f)') (cfc(I),I=1,3)
		 write(1001,'(10f)') (etc(I),I=1,10)
		 write(1001,'(3f)') (efc(I),I=1,3)
	     write(1001,'(20("*"),a,20("*"))') 
     &      '  CURVES Available for RESDH in TYPE141  '
	   do j=1,nResDH
		 write(1001,'(a60)') ResDHcoef_txt(j)
		 write(1001,'(4f)') (A1(I,j),I=1,4)
		 write(1001,'(4f)') (B1(I,j),I=1,4)
		 write(1001,'(4f)') (C1(I,j),I=1,4)
		 write(1001,'(4f)') (t_rng1(I,j),I=1,2),(rh_rng1(I,j),I=1,2)
	   enddo
	     write(1001,'(20("*"),a,20("*"))') 
     &      '  CURVES Available for DESDH in TYPE141  '
	   do j=1,nDesDH
		 write(1001,'(a60)') DesDHcoef_txt(j)
		 write(1001,'(4f)') (A2(I,j),I=1,4)
		 write(1001,'(4f)') (B2(I,j),I=1,4)
		 write(1001,'(4f)') (C2(I,j),I=1,4)
		 write(1001,'(4f)') (D2(I,j),I=1,4)
		 write(1001,'(4f)') (t_rng2(I,j),I=1,2),(rh_rng2(I,j),I=1,2)
         enddo
	  close(1001)
      endif

c     Define PARAMETERS
c
      isys = INT(PAR(1))            ! system number
      ipflag = INT(PAR(2))          ! print flag

c       All other parameters defined below
c
      Tpin = Xin(1)           ! Process inlet Temp (F)
      wpin = Xin(2)           ! Process inlet humidity (lb/lb)
      mdot = Xin(3)           ! Process INLET flow (lb/hr)
      Trin = Xin(4)           ! Regeneration Temperature (F)
      wrin = Xin(5)           ! Regeneration humidity (lb/lb)
	RTFd = Xin(6)			! Run time fraction of unit


c
c     call psych to get WB of incoming air (if needed)
      IF (isys .eq. 7) then
        psydat(1) = 1
        psydat(2) = Xin(1)
        psydat(6) = Xin(2)
        mode = 4
        wbmode = 1
	  iunits=2
        CALL PSYCHROMETRICS(TIME,INFO,IUNITS,MODE,WBMODE,PSYDAT,EMODE,
	1	ISTAT)
        Tpwb = psydat(3)       ! Process Inlet Wet-Bulb Temperature (F)
	ELSE
	  Tpwb =0.
	END IF
c

      IF (ipflag .gt. 100) THEN               ! ipflag is a time trip
         IF (INT(time) .ge. ipflag) THEN
          ipflag = 13
          ELSE
          ipflag = 0
         END IF
      END IF

      scfm = mdot/(0.075*60.)		! process air (supply) cfm
      fanef = .5					! fan efficiency
      mtref = .85					! motor efficiency

c
      IF (isys .eq. 0) THEN       !******* Null Unit ********************
          tkw = 0.
	    W_cfm = DBLE(Par(3))
          wattp = W_cfm*scfm
          tkw   = wattp/1000.
          wpo = wpin 
          tpo = Tpin + wattp*3.413/(mdot*0.241)  !add in fan heat
      ENDIF                                             

c
      
      IF (isys .eq. 1) THEN       ! ******* Albers (isys=1) *********************
          call Albers(Tpin,wpin,Trin,wrin,scfm, 
     &                Qs,Ql,Gas,tkw,wattp)
          wattp = wattp*1000. ! convert to Watts 
          wpo = wpin - Ql*1000./(4770.*scfm)  
          tpo = Tpin - Qs*1000./(1.08*scfm)
      ENDIF
            
      IF (isys .eq. 2) THEN       !******* DC-026 ICC Gas Unit (isys = 2) **********
          i = 0
          Call ICC(i,Tpin,wpin,Trin,wrin,scfm, Qs,Ql,Gas,tkw,wattp)
          wattp = wattp*1000. ! convert to Watts 
          wpo = wpin - Ql*1000./(4770.*scfm)  
          tpo = Tpin - Qs*1000./(1.08*scfm)
c          write(23,'(2(f6.2,f8.5))') Tpin,wpin,Trin,wrin
c          write(23,'(f6.2,f10.5,2(f8.1))') Tpo,wpo,Ql,Qs
          if (wpo .le. 0) then
            Ql = 4.770*scfm*(wpin-0.0001)
c            Qs  = Qs*qln/ql 
            wpo = wpin - Ql*1000./(4770.*scfm)  
            tpo = Tpin - Qs*1000./(1.08*scfm)
          endif
c          write(23,'(f6.2,f10.5,2(f8.1))') Tpo,wpo,Ql,Qs
          tkw = 1.7*scfm/1000.
          wattp = tkw*.47*1000.
      ENDIF                         
      
      if ((isys .eq. 3) .or. (isys .eq. 4)) then !** Silica/ Type 1M (isys=3,4) ***
          warea  = 2000./400./.75
          gasef  = 0.9
          Tri    = 284.0
          pfanef = 0.25
          rfanef = 0.25
          mtrefc = 0.70 
          dpth   = 8.25                            
          heff   = 0.85             
          isiz   = 1               
          evapefp = 0.
          evapefr = 0.85      
          if (info(7) .eq. -1) then
            isiz=0
            tpin = trin
            wpin = wrin
          endif
          zed  = 0.0d0
          ized = 0                      
          aone = 1.0d0                                     
    
c          Call ADL(Trin,wrin,Tpin,wpin,scfm,isys,aone,aone,
c     &             ized,zed,aone,zed,zed,heff,dpth,ipflag,isiz,
c     &            Qs,Ql,tkw,gas,vcfm,aqs,aql,akw,rkw,pkw)

          tkw = 1.7*scfm/1000.
          wattp = tkw*.47*1000.
          wpo = wpin - Ql*1000./(4770.*scfm)  
          tpo = Tpin - Qs*1000./(1.08*scfm)
      endif

      if (isys .eq. 5) then     ! **** Enthalpy wheel, balanced isys=5) ******
	    eff   = DBLE(Par(3))
	    W_cfm = DBLE(Par(4))
	    W_cfm2= DBLE(Par(5))
          wattp = W_cfm*scfm
          tkw   = (W_cfm+W_cfm2)*scfm/1000.   !total unit power
          Tpo   = Tpin + (Trin-Tpin)*eff + wattp*3.413/(mdot*0.241)
          wpo   = wpin + (wrin-wpin) * eff
          Qs    = 1.08  * scfm * (Tpin - Tpo)/1000.0
          Ql    = 4770. * scfm * (wpin - wpo)/1000.0 
          gas   = 0.0
      endif

      IF (isys .eq. 6) THEN       !******* DB-025 ICC Ele Unit (isys=6) *********
          i = 0
          Call ICC_ELE(i,Tpin,wpin,Trin,wrin,scfm,
     &                 Qs,Ql,tkw,wattp)
          wattp = wattp*1000. ! convert to Watts 
          wpo = wpin - Ql*1000./(4770.*scfm)  
          tpo = Tpin - Qs*1000./(1.08*scfm)
          if (wpo .le. 0) then
            Ql = 4.770*scfm*(wpin-0.0001)
            wpo = wpin - Ql*1000./(4770.*scfm)  
          endif
      ENDIF                         

      IF (isys .eq. 7) THEN       !******* Addison Fresh-Air Unit (isys=7)  *****
          CALL Addison(Tpin, Tpwb, wpin, scfm, Qs, Ql, tkw, Wattp)
          wattp = wattp*1000. ! convert to Watts 
          wpo   = wpin - Ql*1000./(4770.*scfm)
          tpo   = Tpin - Qs*1000./(1.08*scfm)
          if (wpo .le. 0) then
            Ql = 4.770*scfm*(wpin-0.0001)
            wpo = wpin - Ql*1000./(4770.*scfm)  
          endif
      ENDIF                         

      IF (isys .eq. 8) THEN       !******* Kathabar (isys=8) ********************
          ktons = DBLE(PAR(3))
          ehx = 0.
          ebrnr = .7
          gas_max=350.*ktons/12.  
          mtref = 0.31
          CALL Kathabar(ktons,Tpin,wpin,Trin,wrin,scfm,fanef,mtref,
     &                Qs,Ql,tkW,Gas,wattp)
          tkw = tkw + 3.18  ! want 2.2 W/cfm, pkw not scaled in routine
          wattp = wattp*1000. ! convert to Watts 
          wpo = wpin - Ql*1000./(4770.*scfm)  ! kathabar exit cond.
          tpo = Tpin - Qs*1000./(1.08*scfm)
      ENDIF                                             

	IF (isys .eq. 9) THEN      !******* Munters Unit (isys=9) ********************
	    iwtype		= INT(Par(10))	! desiccant wheel type
	    wdiam		= 48			! desiccant wheel diameter (inches)
	    wfrac		= 0.75			! fraction of wheel exposed to process air
          shx_eff		= DBLE(Par(6))  ! Sensible HX efficiency
	    shx_leak	= DBLE(Par(9))	! Sensible HX moisture leakage (fraction)
	    evp_eff		= DBLE(Par(7))  ! evap cooler effectiveness
	    Wcfm_p		= DBLE(Par(4))  ! Process Fan Power (W/cfm)
	    Wcfm_r		= DBLE(Par(5))  ! Regen Fan Power (W/cfm)
	    TONS_rat_pc	= DBLE(Par(3))  ! Post cooling coil Capacity (tons)
	    EER_rat_pc	= DBLE(Par(11))	! rated EER of post cooling coil (Btuh/w)
		SHR_rat_pc	= DBLE(Par(12))	! rated sensible heat ratio of post clg coil
	    pc_cntl		= DBLE(Par(8))  ! post cooling control mode

          If (shx_eff .gt. 0.) THEN 
	      rcfm		= scfm			! regen air flow (cfm)  ASSUME balanced with HX
          ELSE
            rcfm		= scfm*(1-wfrac)/wfrac ! ASSUME same face velocity on regen side
		ENDIF

		CALL Munters(ipflag,Tpin,wpin,scfm,trin,wrin,iwtype,wdiam,
     &	  wfrac,shx_eff,shx_leak,evp_eff,rcfm,wcfm_p,wcfm_r,tons_rat_pc,
     &	  eer_rat_pc,shr_rat_pc,pc_cntl,
     &	  Tpo,wpo,qreac,scfmo,kw_t,kw_sfan,gas)

		Tpo = Tpo
		wpo = wpo
		tkw = kw_t
		wattp = Wcfm_p*scfm						! Supply/Process Fan Power (Watts)
		Qs = 1.08*scfm*(Tpin-Tpo)/1000.			! MBtuh Sensible Load
		Ql = 4770.*scfm*(wpin-wpo)/1000.		! MBtuh Latent Load

	ENDIF

	IF (isys .eq. 10) THEN		!******* Drykor Unit (isys=10)********************
	    no_of_units = Par(3)	! no of 7.5H units
	    W_cfm  = Par(4)
	    W_cfm2 = Par(5)
	    scfm0 = scfm/no_of_units
		CALL Drykor (Tpin,wpin,scfm0,SHR,COP,QT0)
		QT=QT0*no_of_units							! scale for larger size
		tkw = QT*0.2931/COP	+ W_cfm2*scfm/1000.	! add in fan power that cycles w/ unit
		wattp = W_cfm*scfm 
		Qs = QT*SHR	- Wattp*3.413/1000.		! MBtuh Sensible Capacity with fan heat
		Ql=QT-Qs							! MBtuh Latent Capacity
		Tpo = Tpin-(Qs*1000.)/(1.08*scfm)
		wpo = wpin-(Ql*1000.)/(4770.*scfm)
	    Gas = 0.

	ENDIF


	IF (isys .eq. 11) THEN		!******* Residential Electric DH Units (isys=11) ********************
	    
c                            PAR(9) is used outside in TRD file to limit DH operation in this mode
		dhtype		= INT(Par(10))	! dehumidifier type (pulls coef sets 1,2, 3.. from RESDH.COF)
	    cfm_nom		= DBLE(Par(3))			! nominal CFM of unit
	    W_cfm		= Par(4)
		CALL Resdh (Tpin,wpin,cfm_nom,dhtype, HA,CAP,ELEC)
		wattp = W_cfm*cfm_nom 
		tkw = ELEC/1000. + W_cfm*cfm_nom/1000.		! add in fan power that cycles w/ unit
		Qs = -HA/1000.-Wattp*3.413/1000.			! MBtuh Sensible Capacity with fan heat
		Ql = CAP*1.060								! MBtuh Latent Capacity
		Tpo = Tpin-(Qs*1000.)/(1.08*scfm)
		wpo = wpin-(Ql*1000.)/(4770.*scfm)
	    Gas = 0.

	ENDIF

	IF (isys .eq. 12) THEN		!******* Desiccant DH Units (isys=12) ********************
	
		dhtype		= INT(Par(10))  ! desiccant type (pulls coef sets 1,2.. from DESDH.COF)
		cfm_nom = DBLE(Par(3))		! nominal CFM of unit
	    W_cfm	= Par(4)

		CALL desdh (Tpin,wpin,cfm_nom,Trin,dhtype,HA,CAP,ELEC,Gas)
		wattp = W_cfm*cfm_nom 
          ELEC = Par(5)*cfm_nom					  ! Watts that cycle on/off with des unit
                                                    ! This power now overides ELEC from desdh 7/6/04

		tkw = ELEC/1000. + W_cfm*cfm_nom/1000.	    ! add in fan power that cycles w/ unit
		Qs = -HA/1000.-Wattp*3.413/1000.			! MBtuh Sensible Capacity with fan heat
		Ql = CAP*1.060								! MBtuh Latent Capacity
		Tpo = Tpin-(Qs*1000.)/(1.08*scfm)
		wpo = wpin-(Ql*1000.)/(4770.*scfm)
		
	ENDIF
	
	IF (isys .eq. 13) THEN      !******* Semco  IADR Unit (isys=13) *******************
	    brnr_eff    = 0.95
	    f_prg		= .05			! purge fraction 
		TONS_rat_pc	= DBLE(Par(3))  ! Cooling coil Capacity (tons)
		Wcfm_p		= DBLE(Par(4))  ! Process Fan Power (W/cfm) 
		Wcfm_r		= DBLE(Par(5))  ! Regen Fan Power (W/cfm) 
		an_units	= DBLE(Par(6))  ! Number of Desiccant Units
		f_byp 	    = DBLE(Par(7))	! bypass fraction (portion of flow that bypasses des whl)
	    pc_cntl		= DBLE(Par(8))  ! post cooling control mode
	    Tris		= DBLE(Par(9))  ! regen temperature setpoint (F)
	    iwtype		= INT(Par(10))	! desiccant wheel type (1-4 for REV-2250 to REV-6000)
	    EER_rat_pc	= DBLE(Par(11))	! rated EER of post cooling coil (Btuh/w) 
		SHR_rat_pc	= DBLE(Par(12))	! rated sensible heat ratio of post clg coil
	    tco_limit   = 45.			! Coil exit can not be less than 45F
		wrset_spt1   = DBLE(Par(13)) ! humidity (lb/lb) where rtf_whl= 0%
		wrset_spt2   = DBLE(Par(14))	! humidity (lb/lb) where rtf_whl=100% 
									! (only used if EER_rat_pc < 0) 
		tas_delta   = DBLE(Par(15)) ! delta temperature for TAS reset schedule
		trset_spt1  = DBLE(Par(16)) ! temperature (F) where TAS set pt is at MAX
		trset_spt2  = DBLE(Par(17)) ! temperature (F) where TAS set pt is at MIN
		reset_var   = DBLE(Par(18)) ! condition used for reset control 
c									  (0=process inlet, 1=regen inlet) 

          If (Tpin .gt. tco_limit) then 
		 CALL Semco(ipflag,Tpin,wpin,scfm,trin,wrin,iwtype,an_units,
     &	  f_prg,f_byp,
     &	  brnr_eff,Tris,wcfm_p,wcfm_r,tons_rat_pc,
     &	  eer_rat_pc,shr_rat_pc,pc_cntl,tco_limit,
     &	  wrset_spt1,wrset_spt2,
     &      tas_delta, trset_spt1,trset_spt2,reset_var,
     &	  Tpo,wpo,scfmo,kw_t,kw_sfan,gas)

		 Tpo = Tpo
		 wpo = wpo
		 tkw = kw_t
		else								! skip Makeup_unit of too cold outside
	      Tpo = Tpin + Wcfm_p*3.413/1.08
	      wpo = wpin
		  tkw = Wcfm_p*scfmo/1000.
	    endif

     		wattp = Wcfm_p*scfmo						! Supply/Process Fan Power (Watts)
		Qs = 1.08*scfmo*(Tpin-Tpo)/1000.			! MBtuh Sensible Load
		Ql = 4770.*scfmo*(wpin-wpo)/1000.			! MBtuh Latent Load
	ENDIF

	IF (isys .eq. 14) THEN      !******* Makeup Air Unit - w/ HGB (isys=14) *******************


c               	14				
c               	Makeup Air unit	
c				***************	
c               	tons_rate_mau	
c               	Wcfm_p			
c               	ishrf			
c               	twet_o			
c               	gam_o
c               	rht_cntl
c				TCL_min
c				n_stg
c				EER_rat_mau
c				SHR_rat_mau


	   TONS_rat_mau	= DBLE(Par(3))  ! Cooling coil Capacity (tons)
		Wcfm_p		= DBLE(Par(4))  ! Process Fan Power (W/cfm)
		ishrf		= DBLE(Par(5))	! enable shr correlation (0-no 1-adjust SHR w/ runtime linear decay)
		twet_o		= DBLE(Par(6))	
		gam_o		= DBLE(Par(7))	
	    rht_cntl	= DBLE(Par(8))  ! Reheat control mode
	    TCL_min		= DBLE(Par(9))  ! Staging & HGB set pt (F)
	    n_stg		= INT(Par(10))	! No of stages
	    EER_rat_mau	= DBLE(Par(11))	! rated EER of post cooling coil (Btuh/w)
		SHR_rat_mau	= DBLE(Par(12))	! rated sensible heat ratio of post clg coil
		tcl			= DBLE(Par(13))
		ANMAX		= DBLE(Par(14))
		NTUo_nom	= DBLE(Par(15))
		toff_p		= DBLE(Par(16)) 
		tp_p		= DBLE(Par(17)) 
		NTUo_P		= DBLE(Par(18))	

	if (time .gt. 1000) then
	continue
	endif

          If (Tpin .gt. TCL_min) then
	      CALL Makeup_unit(ipflag,Tpin,wpin,scfm,Trin,wcfm_p,
     &      tons_rat_mau,EER_rat_mau,SHR_rat_mau,TCL_min,n_stg,rht_cntl,
     &       tpo,wpo,scfmo,kw_t,kw_sfan,gas)
     	
		  Tpo = Tpo
		  wpo = wpo
		  tkw = kw_t
	    else								! skip Makeup_unit of too cold outside
	      Tpo = Tpin + Wcfm_p*3.413/1.08
	      wpo = wpin
		  tkw = Wcfm_p*scfmo/1000.
	    endif

		wattp = Wcfm_p*scfmo					! Supply/Process Fan Power (Watts)
		Qs = 1.08*scfmo*(Tpin-Tpo)/1000.		! MBtuh Sensible Load
		Ql = 4770.*scfmo*(wpin-wpo)/1000.		! MBtuh Latent Load


		IF (ishrf .eq. 2) THEN       ! adjust SHR w/ runtime linear decay
		  twet_cap = 9999.
		  Ql_rated = TONS_rat_mau*12000.*(1.-SHR_rat_mau)    ! Btuh
		  Mo = twet_o*Ql_rated/(1060.*3600.)    !lbs
		  twet = DMIN1(Mo*3600.*1060./(Ql+1.0d-25), twet_cap)  ! cap twet
									 !HH 3/30/95
					
			if (NTUo_nom.EQ. 0) THEN		!KBK 12/20/05 added conditional calculation
				gamma = DMIN1(gam_o*Ql_rated*(Tpin-Tpwb)/
	1		                                 (13.*Ql+1.0d-25),100.d0)     ! 1/24/05
			else
				tp = Mo*1060/(1.08*scfm*(Tpin-Tpwb))*3600
				NTUo = NTUo_nom * (450 * TONS_rat_mau)**2/(scfm)**0.2
			endif

			Qtot = Qs + Ql
			shro = Qs/(Qtot+1.0d-25) 
			Qs=Qtot*FSHR(1.0d0,shro
	1	       ,gamma,tp,twet,anmax,tcl,RTFd,NTUo,toff_p,tp_p,NTUo_P)
			Ql = Qtot - Qs
		ENDIF
	ENDIF

	IF (isys .eq. 15) THEN      !******* Munters HCU (isys=15) *******************
	    iwtype		= INT(Par(3))   ! HCU model number 1=1004, 2=2008, 3=2010, 4=3012,
c													   5=4016, 6=4020, 7=6030, 8=8040
		Wcfm_p		= DBLE(Par(4))  ! Process Fan Power (W/cfm) 
		no_of_units = DBLE(Par(5))	! Number fo HCU Units
	    T_on_stg1   = DBLE(Par(6))  ! Temperature for Stage 1
	    T_on_stg2   = DBLE(Par(7))  ! Temperature for Stage 2
c						   Par(8-12)! Not used

          istg = 0					! unit stage is 2 if Tpin > T_on_stg1
									! unit stage is 1 if T_on_stg1 < Tpin < T_on_stg2 

          If (Tpin .gt. T_on_stg1) then 
	      istg = 1
	      if (Tpin .gt. T_on_stg2) istg = 2
	      CALL HCU (ipflag,Tpin,wpin,scfm,Trin,istg,iwtype,wcfm_p,
     &       no_of_units,
     &       tpo,wpo,scfmo,kw_t,kw_sfan)     	
		  Tpo = Tpo
		  wpo = wpo
		  tkw = kw_t
	    else								! skip Makeup_unit of too cold outside
	      Tpo = Tpin + Wcfm_p*3.413/1.08
	      wpo = wpin
		  tkw = Wcfm_p*scfmo/1000.
	    endif

		wattp = Wcfm_p*scfmo					! Supply/Process Fan Power (Watts)
		Qs = 1.08*scfmo*(Tpin-Tpo)/1000.		! MBtuh Sensible Load
		Ql = 4770.*scfmo*(wpin-wpo)/1000.		! MBtuh Latent Load
          Gas = 0.								! no gas use
	ENDIF
	
c	write(55,*) '108 Outputs:',Tpo,wpo,tkw,gas,qs,ql

      Out(1) =  (Tpo)                ! Leaving air temp (F) with proc fan heat
      Out(2) =  (wpo)                ! Leaving air humidity (lb/lb)
      Out(3) =  (tkw-wattp/1000.)    ! total power w/o Proc.Fan (kW)
      Out(4) =  (Qs*1000.)           ! net sensible (Btu/h) with proc fan heat
      Out(5) =  (Ql*1000.)           ! net latent  (Btu/h)
      Out(6) =  (wattp/1000.)	       ! Process Fan Power (kW)
      Out(7) =  (Gas)                ! Gas input (kBtu/h) 


      RETURN 1
      END