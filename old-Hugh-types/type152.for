      SUBROUTINE TYPE152 (TIME,XIN,OUT,T,DTDT,PAR,INFO,ICNTRL,*)

C     This routuine is a SHORT TIMESTEP CONTROLLER
c     Now has HIGH STAGE flag for two Speed AC Units (May 2011)
c	for simulations with time steps on the order of 0.01 hrs (36 sec) or 0.02 hrs (72 sec).  
c	It looks at the space conditions (Tin, RHin, Cin) and operating states (RTFs) 
c	from the last timestep and decides when the equipment state should be changed
c
c     The routine will include detailed Tstat calcs (from Henderson 1992)
c     It also keeps track of the equipment on times and off times
c 
c	PARAMETERS
c	1	ipflag	- flag to initiate printing
c	2	STG_Delay - The delay time for High STG to be activated  
c	3	REHEAT  - (1=ON) flag for when rheat is used (instead of DEHUMID)
c	4	rh_offset- Offset of reheat set point ((below the cooling set point)
c	5	OVR_cool - Overcooling factors (max reduction in cooling set point)
c	6	RH_gain  - gain factor (%RH per ^F) to adjust RHmax Set pt
c	7	T_gain	- gain factor (^F per %RH) to adjust Tmax Set pt
c
c	8	T_dbnd	- Tstat temperature deadband (^F) 1/2 above & 1/2 below
c	9	Ta_o	- Anticipator gain (^F)
c	10	tau_a - Anticpator time constant (input as sec)
c	11	tau_b- bimetal element time constant (input as sec)
c
c	12	HUM_dbnd - Humidistat deadband 1/2 above and 1/2 below
c	13	C_dbnd	- CO2 conc deadband 1/2 above and 1/2 below
c
c    14-20  AC FAN (5):	 (Cntl_type , Time_ON, Time_OFF, Interlock 1, 2 & 3, Sched #)
c    21-27 Des FAN (6):	""
c    28-34 Vnt FAN (7):	""
c    35-41 Exh FAN (8)	""
c    42-48 HRV/ERV (9)
c						Cntrl_type:   0 - none, 1 - Always ON, 2 - schedule, 3 - DUTY cycle, 4 - Serial ON/OFF
c						Time_ON:	minimum ON time (in hours, multiple of time step)
c						Time_OFF:	minimum OFF time (in hours, multiple of time step)
c						Interlocks:  index of device to interlock with (must always be a lower index)
c						Schedule:	index of schedule to use from Fan_sched.COF (1-10)
c
c	INPUT VARIABLES
c	1	Tin		- temperature control variable
c	2	TMIN	- heating set point temperature
c	3	TMAX	- cooling set point temperature
c	4	RHin	- humidity control variable (dewpt or %RH)
c	5	RHMAX	- dehumidification set point 
c	6	Cin		- CO2 vent control variable
c	7	Cmax	- ventilation CO2 set point
c
c	OUTPUT VARIABLES
c	1	RTFh	- heating equipment status (0=OFF, 1=ON)
c	2	RTFc	- cooling equipment status (0=OFF, 1=ON)
c	3	RTFd	- dehum/rht equipment status (0=OFF, 1=ON)
c	4	RTFv	- ventilation equipment status (0=OFF, 1=ON)
c	5	TIME	- TRNSYS time (hrs)
c	6	Tin		- space temperature
c	7	RHin	- space humidity
c	8	Cin		- CO2 concentration
c	9	T_ON_h	- On time for heating equip (hrs)
c	10	T_OFF_h	- Off time for heating equip (hrs)
c	11	T_ON_c	- On time for cooling equip (hrs)
c	12	T_OFF_c	- Off time for cooling equip (hrs)
c	13	T_ON_d	- On time for dehumid equip (hrs)
c	14	T_OFF_d	- Off time for dehumid equip (hrs)
c	15	T_ON_v	- On time for ventilation equip (hrs)
c	16	T_OFF_v	- Off time for ventilation equip (hrs)
c	17	Ta		- anticipator temperature rise (F)
c	18	Te		- bimetal element temperature (F)
c	19	RTFacf	- AC FAN equipment status (0=OFF, 1=ON)
c	20	RTFdf	- Dehum FAN equipment status (0=OFF, 1=ON)
c	21	RTFvf	- Vent FAN equipment status (0=OFF, 1=ON)
c	22	RTFxf	- Exh FAN equipment status (0=OFF, 1=ON)
c	23	RTFhf	- HRV FAN equipment status (0=OFF, 1=ON)
c    24  Hi_STG_c - High Stage Flag (0 = low stage, 1 = High Stage)
c	25   fhz     - AC speed signal (0-1).  Equals zero when OFF.  Starts out at 0 
c
c
c								(Reheat=0)					(Reheat=1)
c								Dehumid Mode				Reheat Mode
c								variable - equip			variable - equip
c								-------------				-----------
c	Heating (RTFh)  Tmin		Tin - heat coil		       Tin - heat coil
c	Cooling (RTFc)	Tmax		Tin - cool coil	   Tin or RHin - cool coil
c	Dehumid (RTFd)	RHmax       RHin - dehumid 			   Tin - reheat coil
c
c	Cooling operation (to meet RHin) is not allowed when Tin < Tmin
C
c    If the OVR_Cool parameter is >0, then the cooling set point is reset 
c    by up to that amount based on the RH.  The Gain parameter:  
c         Overcooling factor  = T_gain * (RHin-RHmax)  <=  1
c    When the Overcooling factor  = 1, the cooling set pt is lowered bt max amount
c
c    Provisions are also provided to set RH setpoint based on T (though no longer used)
c    (As of Mar-23-07 the reheat flag (Reheat=1) no longer must be set) 
c
c    To model the Carrier Thermidistat:
c	   1) OVR_Cool=3, to overcool the space by up to 3F
c	   2) T_gain=0.1667, Reseting the cool setpt by 100% (of OVR_Cool) when RH is 6% of above set pt
c	   3) What happens in TRNSYS Deck:  c            - Limit RTFc < 0.5 when space in lower than cooling set point
c
c	To model the Lennox Humiditrol:
c	   1) OVR_Cool=4, to overcool the space by up to 4F
c	   2) T_gain=5.0,    Reseting the cool setpt by 100% (of OVR_Cool) when RH is 0.2% of above set pt
c	   3) What happens in TRNSYS Deck:  
c	      -the change in mode (jpbON) for the AC unit happens outside Type 152 
c		   when cooling load is satisfied (i.e., when Tin < Tmax)
c
c
C    REQUIRED BY THE MULTI-DLL VERSION OF TRNSYS
      !DEC$ATTRIBUTES DLLEXPORT :: TYPE152				!SET THE CORRECT TYPE NUMBER HERE

	Implicit none
	INTEGER*4 INFO(15),ICNTRL
      double precision XIN(7),PAR(50),OUT(52),TIME, T, DTDT
	double precision RTFh,RTFc,RTFd,RTFv,Tin,RHin,Cin,
     & RTFh_last,RTFc_last,RTFd_last,RTFv_last,Tin_last,TIME_last,
     & RHin_last,Cin_last,Tmax,Tmin,RHmax,Cmax,Tmax0,RHmax0,
     & reheat,rht_offset,OVR_cool,T_gain,RH_gain,
     & T_dbnd,RH_dbnd,C_dbnd,
     & Ta_o,tau_a,tau_b,Ta,Te,Ta_last,Te_last,dt,
     & T_ON_h,T_ON_c,T_ON_d,T_ON_v,T_OFF_h,T_OFF_c,T_OFF_d,T_OFF_v,
     & T_top,T_bot,RH_top,RH_bot,a0,b0,Tcntl,dT_ovr,
     & Hi_STG_c,Hi_STG_c_last, STG_delay,
     & fhz,fhz0,fhz_last, fhz_pgain,fhz_igain,sum_err,sum_err_last,err
	integer ipflag
	
	Integer i,j,ihr,ii
	logical throw_away(9), desire_cooling
	Integer rtf_vector(9),Ilock(9,3),
     &		Cntl_type(9),fschd(9),fan_sched_data(10,24),ifsch,
     &		rtf_vector_last(9),cd_counter(9)
      double precision time_when_OFF(9),time_when_ON(9),cum_on_tim(9),
     &		Time_OFF(9),Time_ON(9)
	double precision duty_tim,tim_into_cycle,tim_remain,dts
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
C


C  FIRST CALL OF SIMULATION
      IF (INFO(7) .EQ. -1) THEN
       CALL TYPECK(1,INFO,7,50,0)  !check no. of inputs, parameters
       INFO(6)=52					! number of outputs
       INFO(9)=1					! Output does depend on time                  
       OUT(1:28)=0.0			! alll current vars = zero
	 OUT(31)=TIME			! last time = starting time	
       OUT(32)=0.				! last Tin = zero  (so we will start in heating in next step) 
       OUT(33)=0.				! last RHin = zero (no dehumid required) 
       OUT(34)=0.				! last Cin eq zero (no vent required)
	 OUT(35:52)=0.


c	  --- read in coefficients for Fan Control Schedule (if data is required)

	 ifsch = par(20)+par(27)+par(34)+par(41)+par(48)
	 If( ifsch .gt. 0) then
		open(unit = 1001,file = "Fan_sched.COF")
		do i=1,10
		 read(1001,'(24i4)') (fan_sched_data(i,j),j=1,24)
		end do
	    close(1001)
	 endif

      ENDIF 

C  Top of Routine
C  
5     CONTINUE

      if (TIME .ne. OUT(5)) then  ! swap in LAST data if TIME advances
	  dt = TIME - OUT(5)		 ! timestep
	  out(27:52) = out(1:26)
      do i=1,9
	 If (cd_counter(i) .gt. 0) cd_counter(i) = cd_counter(i) - 1
	enddo
	endif
	           
      RTFh_last=out(27)
      RTFc_last=out(28)
      RTFd_last=out(29)
      RTFv_last=out(30)

      TIME_last=out(31)
      
	tin_last =out(32)
      RHin_last=out(33)
      Cin_last =out(34)

	Ta_last = out(43)
	Te_last = out(44)
      rtf_vector_last(5:9) = out(45:49)
	Hi_STG_c_last = out(50)
	fhz_last = out(51)
      sum_err_last = out(52)

      Tin   = xin(1)
      Tmin  = xin(2)           
      Tmax0  = xin(3)   
      RHin  = xin(4)
      RHmax0 = xin(5)
	Cin	  = xin(6)
	Cmax  = xin(7)

      ipflag = par(1)
	STG_delay = par(2)      ! delay time for STG 2 cooling (hrs)  - May 2011
      reheat = par(3)			! reheat flag (1=ON)
      rht_offset  = par(4)	! offset of RHT Temp set point					Thermidistat        Lennox
	OVR_cool  = par(5)      ! overcooling factor								3					2 or 4
	RH_Gain = par(6)        ! gain factor (%RH per ^F) to adjust RHmax			0                   0
	T_Gain = par(7)         ! gain factor (^F per %RH) to adjust Tmax			0.1667				5
	T_dbnd  = par(8)		! thermostat deadband (^F)
	Ta_o = par(9)						! anticipator gain (^F)
	tau_a = max(par(10)/3600.,1.0e-11)	! anticipator time constant (input as sec)
	tau_b = max(par(11)/3600.,1.0e-10)	! bimetal element time constant (input as sec)
	RH_dbnd = par(12)		! Humidistat deadband
	C_dbnd = par(13)		! ventostat deadband		All deadbands 1/2 above and 1/2 below set point

	ii=0
	do i=5,9 
       Cntl_type(i) = int(abs(par(14+ii)))
	 if (int(par(14+ii)) .eq. -3) then
	   throw_away(i) = .false.
	 else
	   throw_away(i) = .true.
	 endif  
       Time_ON(i)  = par(15+ii)
       Time_OFF(i) = par(16+ii)
	   do j=1,3
           ilock(i,j) = int(par(16+j+ii))
	   enddo
       fschd(i) = int(par(20+ii))
       ii=ii+7
	enddo

	fhz_pgain = par(49)
	fhz_igain = par(50)

c	Thermostat calcs from Henderson 1992 (used for COOLING ONLY)

	a0 = Tin_last
	b0 = (Tin - Tin_last)/dt
	
	If (Ta_o .gt. 0) then 
	  Ta = Ta_o*(1.-RTFc)*(1.-exp(-dt/tau_a))
     &		+ Ta_last*exp(-dt/tau_a)
	else
	  Ta=0.
	endif
	If (tau_b .gt. 0. .and. TIME .gt. 0.) then
	  Te = (Ta_o*(1.-RTFc) + a0 - b0*tau_b)*(1.-exp(-dt/tau_b))
     &   +  Te_last*exp(-dt/tau_b) + b0*dt
     &   +  (Ta_last-Ta_o*(1.-RTFc))*tau_a						! fixed error in 1992 paper
     &      *(exp(-dt/tau_a)-exp(-dt/tau_b))/(tau_a-tau_b)
     	else
	  Te = Tin
	endif

	IF (OVR_cool .gt. 0.) then							
	   RHmax = RHmax0 + RH_gain*min(max(Tmax0-Tin,0.),OVR_cool)   ! reset RH setpt
	   Tmax = Tmax0 - min(T_Gain*max(RHin-RHmax0,0.),1.)*OVR_cool ! reset T setpt
	ELSE
	   Tmax = Tmax0
	   RHmax = RHmax0
	ENDIF
        
	   dT_ovr = Tmax0 - Tmax	! Amount of "overcooling" (F)
	               
c HEATING CONTROL
      if ((tin_last .le. (Tmin-0.5*T_dbnd)) 
     &				.and. (RTFh_last .eq. 0.0)) then	! switch heat ON
	  RTFh = 1.
	  time_when_ON(1) = TIME_last
	endif
	
      if ((tin_last .ge. (Tmin+0.5*T_dbnd)) 
     &				.and. (RTFh_last .eq. 1.0)) then ! switch heat OFF
	  RTFh = 0.
	  time_when_OFF(1) = TIME_last
	endif
	                                
c COOLING CONTROL -------------------------------------(use Te_last instead of Tin_last)
       T_top  = Tmax + 0.5*T_dbnd		! top of band
	 T_bot  = Tmax - 0.5*T_dbnd 
       RH_top = RHmax + 0.5*RH_dbnd
	 RH_bot = RHmax - 0.5*RH_dbnd
	  
       Tcntl = Te_last

	if (reheat .eq. 0) then
	  if ( Tcntl .lt. T_bot+dT_ovr .and. Tcntl .gt. T_bot .and. desire_cooling  ) then		!---------Overcooling Mode AND T < clg spt
! desire_cooling added Aug-23-2011 DMB ; don't cycle on until we hit top of deadband again
          if (RTFc_last .eq. 1 .and.								! HIH Aug-22-2011
     &			(TIME_last - time_when_ON(2)) .gt. 0.16 )then	!If its been ON for 9.6 minutes, turn it OFF 
              RTFc = 0.
	        time_when_OFF(2) = TIME_last
	    endif
          if (RTFc_last .eq. 0 .and. 
     &			(TIME_last - time_when_OFF(2)) .gt. 0.16 )then	!If its been OFF for 9.6 minutes, turn it ON
              RTFc = 1.
	        time_when_ON(2) = TIME_last
	    endif
	  else														! -------- Normal cooling logic
          if ( (Tcntl .ge. T_top) 
     &				.and. (RTFc_last .eq. 0.0)) then	! switch cool ON
               desire_cooling = .true.   ! used by cycle logic, above
	       RTFc = 1.
	       time_when_ON(2) = TIME_last
	     endif
	
           if ((Tcntl .le. T_bot) 
     &				.and. (RTFc_last .eq. 1.0)) then ! switch cool OFF
                desire_cooling = .false.
	        RTFc = 0.
	        time_when_OFF(2) = TIME_last
	     endif
	  endif
	else																! ------ REHEAT Mode
        if ((Tcntl .ge. T_top) .or. (RHin_last .ge. RH_top) 
     &				.and. (RTFc_last .eq. 0.0)) then	! switch cool ON
	      RTFc = 1.
	      time_when_ON(2) = TIME_last
	   endif
	
         if ((Tcntl .le. T_bot) .and. (RHin_last .le. RH_bot)
     &				.and. (RTFc_last .eq. 1.0)) then ! switch cool OFF
	      RTFc = 0.
	      time_when_OFF(2) = TIME_last
	   endif
         if ((Tcntl .le. Tmin)
     &				.and. (RTFc_last .eq. 1.0)) then ! switch cool OFF if Heating setpt is reached
	      RTFc = 0.
	      time_when_OFF(2) = TIME_last
	   endif
      endif
c     ----------------------------- High stage cooling control (2-speed) (May 2011)
c	High Stage is activated when the temperature is at or above the top of the set point band -5%)
c     AND the cooling ON time is greater than Stage Delay time (hrs). The delay time is only used the first time 
c	High Stage is turned off when the temperature drops to the middle of the deadband (-5%). 
c	Subsequent High/Low cycles just require Temp to activate/deactivate

	if (Tcntl .ge. (T_top-0.05*T_dbnd) 
     &		.and. (OUT(37)) .gt. STG_delay) then	! OUT(37) is last T_ON_C (on time)
			Hi_STG_c = 1
 
	endif
      if (Tcntl .lt. (Tmax-0.05*T_dbnd).and. Hi_STG_c_last .eq. 1) then
			Hi_STG_c = 0
	endif 

c	------------------------------ Variable Speed control ---------------------------
c	Increment last fractional hz up or down by [T error fraction] x gain
c	where Tmax is the center of the deadband (the "target")
c	At the max error the max change is  fhz_pgain x 0.5 
	
		    
	if ((OUT(37)) .gt. STG_delay) then				! OUT(37) is last T_ON_C (on time)
	  err = (Tcntl-Tmax)/T_dbnd
        sum_err = sum_err_last + err
	  fhz0 = sum_err*fhz_igain + fhz_pgain*err
	  fhz = MIN(MAX(fhz0 , 0.), 1.)
	  sum_err = min(sum_err,(1.- fhz_pgain*err)/fhz_igain)
	  sum_err = max(sum_err,(0.- fhz_pgain*err)/fhz_igain)
	else
	  fhz = 0.
	  sum_err = 0.
      endif
	fhz = fhz*RTFc

C HUMIDITY CONTROL

	if (reheat .eq. 0) then
        if ( (RHin_last .ge. RH_top) 
     &		.and. (RTFd_last .eq. 0.0) .and. (OVR_cool .eq. 0.)) then	! switch dehumid ON
	      RTFd = 1.														! (Only if OVR_cool = 0)
	      time_when_ON(3) = TIME_last
	   endif
	
         if ((RHin_last .le. RH_bot) 
     &				.and. (RTFd_last .eq. 1.0)) then ! switch dehum OFF
	      RTFd = 0.
	      time_when_OFF(3) = TIME_last
	   endif
	else															! REHEAT Mode
        if ((tin_last .le. T_bot-rht_offset) 
     &	        .and. (RTFd_last .eq. 0.0)
     &			.and. (OVR_cool .eq. 0.).and. (RTFc .eq. 1.0)) then	! switch Reheat ON
	      RTFd = 1.													!(Only if No OVR_cool & Cooling is ON)
	      time_when_ON(3) = TIME_last
	   endif
	
         if ((tin_last .ge. T_top-rht_offset) 
     &				.and. (RTFd_last .eq. 1.0)) then ! switch reheat OFF
	      RTFd = 0.
	      time_when_OFF(3) = TIME_last
	   endif
      endif

      if (reheat .eq. 1 .and. rtfc .eq. 0.) rtfd=0.   ! no cooling then no reheat
      if (OVR_Cool .gt. 0 )  rtfd=0.0					! No reheat or DH in Overcooling mode

c VENTILATION CONTROL

      if ((Cin_last .ge. (Cmax+0.5*C_dbnd)) 
     &				.and. (RTFv_last .eq. 0.0)) then	! switch vent ON
	  RTFv = 1.
	  time_when_ON(4) = TIME_last
	endif
	
      if ((Cin_last .le. (Cmax-0.5*C_dbnd)) 
     &				.and. (RTFv_last .eq. 1.0)) then ! switch vent OFF
	  RTFv = 0.
	  time_when_OFF(4) = TIME_last
	endif

********************************** Fan Control Logic ***************************
c		all 'time' & 'tim' variables are in fractional hours

	rtf_vector(1) = rtfh
	rtf_vector(2) = rtfc
	rtf_vector(3) = rtfd
	rtf_vector(4) = rtfv

	dts = dt/10.
	do i=5,9
	  rtf_vector(i)=0
c----------------------------------------------- none (w/ optional fan delay)

       if (Cntl_type(i) .eq. 0 .and. Time_ON(i) .gt. 0) then	! fan delay after cooling (2)
	   If ((TIME-time_when_OFF(2)-dts) .lt. Time_ON(i) .and. 
     &	       time_when_OFF(2) .gt. time_when_ON(2)) then
		    RTF_vector(i) = 1
	   endif
	 endif
c-----------------------------------------------  Always ON (w/ optional draindown time)
	 if (Cntl_type(i) .eq. 1) then
	   rtf_vector(i) = 1
	   If ((TIME-time_when_OFF(2)-dts) .lt. Time_OFF(i) .and. 
     &	       time_when_OFF(2) .gt. time_when_ON(2)) then
	     RTF_vector(i) = 0
	   endif
	 endif	
c-----------------------------------------------  Schedule
	 if (Cntl_type(i) .eq. 2 .and. fschd(i) .gt. 0) then
	    ihr = mod(int(Time),24)
		rtf_vector(i) = fan_sched_data(fschd(i),ihr)	! use schedule
	 endif

c----------------------------------------------- Final Application of Interlocks
	 do j=1,3				! Apply the Interlocks
	   if (ilock(i,j) .gt. 0) then
	    if (rtf_vector(ilock(i,j))  .eq. 1) rtf_vector(i) = 1
	   endif	
	   if (ilock(i,j) .lt. 0) then 
	    if (rtf_vector(-ilock(i,j)) .eq. 0) rtf_vector(i) = 1 
	   endif 	
	 enddo
	if (rtf_vector(i) .eq. 1) cd_counter(i)=0		! operation for other reasons clears the counter
c-----------------------------------------------  dutycycle control	
	 if (Cntl_type(i) .eq. 3) then					 
	    duty_tim = Time_ON(i)+Time_OFF(i)
	    tim_into_cycle = mod(TIME,duty_tim)
	    tim_remain = duty_tim - tim_into_cycle
	    if ( TIME .ne. OUT(5) ) then				! or info(7) eq zero?
	      if (tim_into_cycle .lt. dts .or. 
     &			tim_into_cycle .gt. duty_tim-dts) then
		   cum_on_tim(i) = 0.
	      else
		   cum_on_tim(i)=cum_on_tim(i) 
     &				+ rtf_vector_last(i)*dt
		  endif
		endif
		if ((Time_ON(i) - cum_on_tim(i)+dts) .gt. tim_remain) then
		  RTF_vector(i) = 1
		  IF (tim_remain .lt. 2.1*dt .and. throw_away(i) 
     &		.and. time_when_OFF(i) .gt. time_when_ON(i))  
     &					RTF_vector(i)=0
		endif
	 endif 
c-----------------------------------------------  series ON/OFF control		
	 if (Cntl_type(i) .eq. 4) then
	    If ((TIME-time_when_OFF(i)-dts) .gt. Time_OFF(i) .and. 
     &	    time_when_OFF(i) .gt. time_when_ON(i)) then
			RTF_vector(i) =1
			cd_counter(i) = int(TIME_ON(i)/dt)
		endif
          IF (cd_counter(i) .gt. 0) RTF_vector(i)=1    
	 endif

c----------------------------------------------- Interlock with limits:  max duty cycle
	 if (Cntl_type(i) .eq. 5 .and. ilock(i,1) .gt. 0) then
	    ii= ilock(i,1)
	    duty_tim = Time_ON(ii)+Time_OFF(ii)
	    tim_into_cycle = mod(TIME,duty_tim)
	    if ( TIME .ne. OUT(5) ) then				! or info(7) eq zero?
	      if (tim_into_cycle .lt. dts .or. 
     &			tim_into_cycle .gt. duty_tim-dts) then
		   cum_on_tim(i) = 0.
	      else
		   cum_on_tim(i)=cum_on_tim(i) 
     &				+ rtf_vector_last(i)*dt
		  endif
		endif
		if ((cum_on_tim(i) + dts) .gt. TIME_ON(i)) then
		  RTF_vector(i) = 0 
		endif
	 endif

c----------------------------------------------- Interlock with limits:  Max Time_ON
	 if (Cntl_type(i) .eq. 6 .and. ilock(i,1) .gt. 0) then
	    ii= ilock(i,1)
	    If ((TIME-time_when_ON(ii)-dts) .gt. Time_ON(i)  
     &	       .and. time_when_ON(ii) .gt. time_when_OFF(ii)) then
              RTF_vector(i)=0
		endif	    
	 endif

C         save time when OFF or ON

       IF (rtf_vector(i) .eq. 1 .and. rtf_vector_last(i) .eq. 0) then
	   time_when_ON(i) = TIME_last 
	 endif
       IF (rtf_vector(i) .eq. 0 .and. rtf_vector_last(i) .eq. 1) then
	   time_when_OFF(i) = TIME_last 
	 endif

	enddo 	                                

c	OUTPUT VARIABLES


	  out(1:4) = rtf_vector(1:4)					! OUT 1-4	rtfh,rtfc,rtfd,rtfv
	
	do i=1,4
	  If (rtf_vector(i) .eq. 1) then				! Out 9-16	ON & OFF times for h, c, d, v
	    out(7+2*i) = TIME - time_when_ON(i)
	    out(7+2*i+1) = 0.
	  else
	    out(7+2*i) = 0.
	    out(7+2*i+1) = TIME - time_when_OFF(i)
	  endif
	enddo

	out(5) = TIME
	out(6) = Tin
	out(7) = RHin
	out(8) = Cin

	out(17) = Ta
	out(18) = Te

	out(19:23) = rtf_vector(5:9)					! OUT 19-23  ON & OFF times for acf, df, vf, xf
	out(24) = Hi_STG_c
	out(25) = fhz
	out(26) = sum_err
	                              
      if (ipflag .gt. 0) then
c        write(123,100) info(7),out(1:52)				! turn this on to get the detailed fort.123 file
c	  write(123,'(7f)') par(14:20)
c	  write(123,'(7f)') par(21:27)
c	  write(123,'(7f)') par(28:34)
c	  write(123,'(7f)') par(35:41)
c	  write(123,'(7f)') par(42:48)
100     format(i4,46f7.2)                    
	endif

      RETURN 1
      END
