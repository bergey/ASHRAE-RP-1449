      MODULE TrnsysData

      use TrnsysConstants

!**********************************************************************************************
! This "data only" module collects declarations of arrays and variables that are accessed by 
!  various TRNSYS kernel and Type subroutines. It was written as an alternative to passing 
!  information back and forth using COMMON blocks as was done in TRNSYS versions prior to the 
!  release of 16. 
!
! Note: Some variables in this module are initialized in a subroutine called InitializeTrnsysData
!       That subroutine is in this file, after the TrnsysData module. 
!       It is called once by the main Trnsys routine
!
! Written By: D. Bradley 05.2001 for TRNSYS 15.1
!
! Revision History:
!  2001.10.00 - DEB:     Added contents of /TYP65/ COMMON BLOCK   
!  2002.07.00 - JWT/DEB: Added remaining COMMON blocks from BLOCKDATA for TRNSYS 16.00.0000.   
!  2004.05.05 - MKu:     Misc changes, added initializeTrnsysData to avoid screwy DATA  
!                         statements that do not work in IVF.
!  2005.07.18 - DEB:     Added TrnsysDebugLibDir.
!  2005.09.20 - DEB/DAA: Added the info of approved examples for demo version
!  2005.10.17 - DAA:     Added TIME_REPORT for time reports in routines
!  2005.01.26 - DAA:     Added the array INCON_ORIG, for use of getConnectedUnitNumber and
!                        getConnectedTypeNumber with Solver 1
!  2006.03.10 - DAA/DEB: Added CheckedLinks (used by Type00).
!  2006.03.27 - JWT/DAA: Added new functions GTWARN,GEWARN,EQWARN,NEWARN
!  2006.12.07 - DAA:     Added labels for Type25 - EES lookup tables
!**********************************************************************************************
! Copyright © 2005 Solar Energy Laboratory, University of Wisconsin-Madison. All rights reserved.
        
      IMPLICIT NONE

      PUBLIC          !All variables placed in this data-only module are 
	                !available to other modules and subroutines.
                      !Thus, all variables in this module must be PUBLIC.

! Switch for TRNSED applications
      logical :: isTrnsed = .false.

! Switch for demo version
      logical :: isDemo = .false.

! TRNSYS directories and filenames (the directory structure is different for TRNSED applications)
      character (len=maxPathLength) :: TrnsysRootDir      = "NotSet" ! Main installation directory, e.g. "C:\Program Files\Trnsys16"
      character (len=maxPathLength) :: TrnsysExeDir       = "NotSet" ! Directory with EXE programs, e.g. "C:\Program Files\Trnsys16\Exe"
      character (len=maxPathLength) :: TrnsysUserLibDir     = "NotSet" ! Directory with User DLL's, e.g.   "C:\Program Files\Trnsys16\UserLib\ReleaseDLLs"
      character (len=maxPathLength) :: TrnsysDebugLibDir    = "NotSet" ! Directory with Debug versions of User DLL's, e.g. "C:\ProgramFiles\DebugDLLs"
      character (len=maxPathLength) :: TrnsysInputFileDir = "NotSet" ! TRNSYS deck file directory, e.g.  "C:\My Projects"
      character (len=maxPathLength) :: DECKN1=' '                    ! TRNSYS deck filename, e.g.  "C:\My Projects\Mydeck.dck"
      character (len=maxPathLength) :: LISTNAME=' '                  ! TRNSYS deck file directory, e.g.  "C:\My Projects\MyDeck.lst"
      character (len=maxPathLength) :: TrnsysDeckName     = "NotSet" ! TRNSYS dekc filename w/o path  

! TRNSYS Release String (found in TRNSYS.ini and read in by Messages)
      character (len=maxDescripLength) :: TrnsysReleaseStr = 
     . '16.xx.xxxx'

C ********* DECLARE ALLOCATABLE ARRAYS FOR USE IN DYNDATA 
      DOUBLE PRECISION, ALLOCATABLE :: X1dd(:,:),X2dd(:,:),X3dd(:,:)
	DOUBLE PRECISION, ALLOCATABLE :: X4dd(:,:),YDATAdd(:),DATAINdd(:)
	INTEGER, ALLOCATABLE :: LUSTORdd(:), IPTdd(:)


C ********* DECLARE ALLOCATABLE ARRAYS FOR USE IN setStorageVars 
      DOUBLE PRECISION StaticXSTORE(nStaticStorageSpots)
      DOUBLE PRECISION, ALLOCATABLE :: DynamicXSTORE(:)
      DOUBLE PRECISION, ALLOCATABLE :: XSTORE(:)
		
C ********* DECLARE ALLOCATABLE ARRAYS FOR USE IN TYPE28 
      INTEGER, ALLOCATABLE :: AlreadySorted28(:)
	INTEGER				 :: n28Units=0
		
C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /CNTRL/
      INTEGER::NCNTRL=0          !THE NUMBER OF CONTROLLERS
      INTEGER::ICNTRL(nMaxUnits) !ARRRY OF CONTROL'S STATES FOR EACH UNIT
      INTEGER::ICPTR(nMaxUnits)  !ARRAY OF POINTERS ON ICNTRL FOR EACH UNIT CONTROLLERS 
	                           !OF UNIT I TAKES ROOM FROM ICNTRL(ICPTR(I))
      INTEGER::NUMBER
      INTEGER::UNITCR(nMaxUnits) !CONTROLLER NUMBER I IS IN THE UNIT UNITCR(I)
      LOGICAL::CALLCR(nMaxUnits) !IF CALLCR(I)=TRUE THEN UNIT NUMBER I HAS TO BE CALLED
                                 !AT LEAST ONCE

      DATA ICPTR/nMaxUnits*1/,ICNTRL/nMaxUnits*0/,UNITCR/nMaxUnits*0/
      DATA CALLCR/nMaxUnits*.FALSE./
	
C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /CONVRG/ 
      INTEGER::NCONVR=50           !number of outputs which are to be accelerated - initially given maximum value
      INTEGER::ICVPTR(nMaxUnits,2) !must be dimensioned by the maximum number of units
                                   !ICVPTR(K,1) points to 1st element in ICVOUT for unit K
                                   !ICVPTR(K,1) points to last element in ICVOUT for unit K
      INTEGER::ICVOUT(50)          !list of output numbers to be accelerated - pointed to by ICVPTR
      DOUBLE PRECISION::CVTOL=1E-6 !absolute difference between last two improved output values
      DOUBLE PRECISION::XS(50)     !\
      DOUBLE PRECISION::XLAST(50)  ! used in SETVAL for secant method convergence acceleration
      DOUBLE PRECISION::GLAST(50)  !/  values held between calls  
	INTEGER::ITER(50)       !number of times this timestep FX has been "improved in SETVAL
      LOGICAL::SM(50)
     
      DATA ICVPTR/nMaxUnits2*0/,GLAST/50*0.0/,ITER/50*0/,ICVOUT/50*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /DEFO/
      INTEGER::IDEF=0
	INTEGER::IDFUN(20)=0
	INTEGER::IDFOUT(20)=0
	INTEGER::IDFEQN(20)=0


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /DELUNT/
      INTEGER::DEL=0                !number of deleted INPUTS
	INTEGER::UNDEL(nMaxUnits)     !array of deleted INPUTS
	LOGICAL::CALL1(nMaxUnits)     !described in exec
	LOGICAL::CALL2(nMaxUnits)     !described in exec
	LOGICAL::CALL3(nMaxUnits)     !described in exec
	LOGICAL::CALL4(nMaxUnits)     !described in exec
	LOGICAL::CALL5(nMaxUnits)     !described in exec
	LOGICAL::CALL6(nMaxUnits)     !is flase if UNIT I has been deleted
	INTEGER::DELEQ=0              !number of deleted EQUATIONS
	INTEGER::DEQPTR(nMaxUnits)    !array of deleted EQUATIONS
	INTEGER::NDELEQ(2*nMaxEquations) !pointer on NDELEQ

      DATA UNDEL/nMaxUnits*0/,CALL6/nMaxUnits*.TRUE./
	DATA CALL1/nMaxUnits*.TRUE./,CALL2/nMaxUnits*.FALSE./
	DATA CALL3/nMaxUnits*.FALSE./,CALL4/nMaxUnits*.FALSE./
      DATA CALL5/nMaxUnits*.FALSE./,DEQPTR/nMaxUnits*0/,
     .     NDELEQ/nMaxEquations2*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /EQTIME/
      INTEGER::IEQTM(nMaxEquations2)=0
	
	
C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /ERRS/
      INTEGER::ITMAX=50  !maximum number of iterations before a warning is generated
      INTEGER::IQTMAX=50 !maximum number of warnings before an error is generated
      INTEGER::ITRACE=50 !number of calls to a component during a timestep before TRACE is turned on.
      INTEGER::ICT=0     !set to 1 by EXEC if a unit has been called more than ITMAX times
      INTEGER::NCALLS=0  !number of component subroutines called
      INTEGER::CALLED(nMaxUnits) !list of units called on the most recent call to exec

      DATA CALLED/nMaxUnits*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /EES/
	CHARACTER*1::EESCALL(maxPathLength,10)=''
	INTEGER::EESUNT(10)

      DATA EESUNT/10*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /EQINFO/
      DOUBLE PRECISION::VALUE(nMaxEquations)		!array of values of EQN variables, dimensioned by MAXEQN
	DOUBLE PRECISION::CONVAL(nMaxConstantsInEquations)		!array of constants appearing in equations 
	                                 !dimensioned by MAXCON
	INTEGER::POLPTR(nMaxEquations+1) !array of pointers: polptr(k)+1 points to the first 
	                           !instruction in POL for equation K
	INTEGER::CONPTR(nMaxEquations+1) !array of pointers: conptr(k)+1 points to the first 
	                           !constant used in EQN k; that constant is CONVAL(CONPTR(K)+1)
							   !POLPTR and CONPTR should be dimensioned by MAXEQN+1
	INTEGER::POL(nMaxEquations*10)   !array of polish notation codes dimensioned by MAXPOL
	INTEGER::IESTAT(nMaxEquations)   !indicates how the variable J is defined:
                                 !0 = constant equation
                                 !1 = equation using only constant equations
                                 !2 = equation depending only on outputs of components
                                 !3 = functions of defined variables
                                 !4 = functions of un-defined variables
	INTEGER::INCON(nMaxUnits*10,2) !used in PROC for mapping but is also used by the equation
                                  !processor to determine which INPUTS refer to variables:
                                  !INCON(K,1) is the unit number of OUTPUT (if any) connected
                                  !to INPUT stored in XIN(K). INCON(K,2) is the corresponding
                                  !OUTPUT number of the connecting output. If INCON(K,2) is
                                  !negative, the INPUT stored in XIN(K) is connected to
                                  !variable number ABS(INCON(K,2)).
                                  !INCON should be dimensioned by the max number of allowable
                                  !INPUTS
      INTEGER::INCON_ORIG(nMaxUnits*10,2) !Copy of INCON.  As INCON is modified when Solver 1
	                            !is used, INCON_ORIG contains the initial information in INCON
	                            !for the use of getConnectedUnitNumber and getConnectedTypeNumber
	INTEGER::MAXPOL=nMaxEquations10     !max number of polish notation codes allowed
	INTEGER::MAXCON=nMaxConstantsInEquations   !max number of constants appearing in equations
	INTEGER::MAXEQN=nMaxEquations     !max number of equations
	INTEGER::NVARS=1            !number of variables defined in EQN cards
	INTEGER::NVARS_MAX=1        !total number of variables defined in EQN and CON cards
      INTEGER::IEQ_ARRAY(nMaxEquations+1)	!Array holding sorted equation pointers

      DATA INCON/nMaxUnits20*0/,CONPTR/nMaxEquationsPls1*0/,
     .     POLPTR/nMaxEquationsPls1*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /EQINF2/
      CHARACTER*1::VNAME(nMaxEquations,maxEqnNameLength)=' ' !array of EQN names; dimensioned by MAXEQN


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /FREX/
      LOGICAL::IFREE(nMaxUnits*10)=.FALSE.


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /FUNJAC/
      INTEGER::INPUNT(nMaxUnits2,2)=0  !DEFINES THE UNIT, WHERE THE VARIABLE I IS AN INPUT
      INTEGER::ITUNIT(nMaxUnits)=0   !THE SAME, BUT FOR DERIVATIVES
      INTEGER::VALXIN(nMaxUnits)=0   !INITIAL VALUE OF UNKNOWN INPUT NUMBER I
      DOUBLE PRECISION::U(nMaxUnits2,2) !KEEP THE VALUE OF THE INPUT, CALCULATED ON PREVIOUS TIMESTEP


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /INCHK/
      CHARACTER*3 YCHECK(nMaxUnits*10)
	CHARACTER*3 OCHECK(nMaxOutputs)
	CHARACTER*3 CHTYP1(nMaxUnitConversions)
      CHARACTER*10 CHTYP2(nMaxUnitConversions)
      
	DATA CHTYP1/nMaxUnitConversions*'NAV'/,
     &     CHTYP2/nMaxUnitConversions*'NAV      '/,
     &     YCHECK/nMaxUnits10*'NAV'/,
     &     OCHECK/nMaxOutputs*'NAV'/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /INCLD/
      INTEGER*4::NXTLINE
	INTEGER*4::NXTLNKEEP

	INTEGER*4::INCLVL
	INTEGER*4::NXTLNMEM(3)


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /IO/
      INTEGER::NINTOT=nMaxUnits10	!TOTAL NUMBER OF INPUTS ALLOWED FOR ALL UNITS
							!(NOT INCLUDING TYPES 24-29)
      INTEGER::INP(nMaxUnits)=1  !LOCATION IN THE XIN ARRAY OF THE FIRST INPUT TO UNIT IU.
      DOUBLE PRECISION::XIN(nMaxUnits*10)=0. !STORES ALL INPUTS SEQUENTIALLY
      DOUBLE PRECISION::XCHECK(nMaxUnits*10)=0. !HOLDS THE INPUT VALUES SO SMALL CHANGES IN XIN OVER TIME GET NOTICED
      INTEGER::OUTMAP(2,nMaxUnits)=0 !OUTMAP(1,IU) POINTS INTO IOUT TO THE 1ST OUTPUT-INPUT
      INTEGER::IOUT(nMaxUnits*10) !CONNECTION OF UNIT IU; OUTMAP(2,IU) POINTS TO THE LAST
      INTEGER::IINDEX(nMaxUnits*10)=0 !SUCH OUTPUT-INPUT CONNECTION. OUTPUT IOUT(K) CONNECTS
      INTEGER::IUNIT(nMaxUnits*10)=0 !TO INPUT (INDEX(K)-INP(IUNIT(K))+1) OF UNIT IUNIT(K).
      DATA IOUT/nMaxUnits10*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /LIST/
      LOGICAL :: ILIST = .TRUE. !variable telling whether a .lst file is desired (true: list)
	INTEGER :: NSAVE = 10     !number of cards to be saved for header
	INTEGER :: UNCHEK(20,2)   !array of unit,input numbers which are not included 
	                          !in convergence checks
	INTEGER :: NUNCHK = 0     !# of unit,input combinations stored in UNCHEK

      DATA UNCHEK/40*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /LOOPCM/
      INTEGER::NLOOPS=0      !number of loops in simulation
	INTEGER :: LPINDX(11)  !array which stores the pointers into LPUNIT for each
	                       !unit LPINDX(K)+1 points to the starting position for loop K
	                       !LPINDX(K+1) points to the final position for loop K
	INTEGER :: LPCALL(10)  !number of unit commands preceeding current loop card
	                       !This is used to determine where the loop should appear
	INTEGER :: LPREPT(10)  !indicates how many repeated calls should be made by each
	                       !loopL LPREPT(K) holds the value for loop K
      INTEGER :: LPUNIT(250) !stores the units in each loop - pointed to by LPINDX

      DATA LPINDX/11*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /LUNITS/
	INTEGER :: LUW   !logical unit for the list file
	INTEGER :: LUR
	INTEGER :: LUK
      INTEGER :: IFORM
	INTEGER :: LUL  ! Logical unit for Log file


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /MAXVAL/
      INTEGER :: IOUTL = 0 !number of outputs in the system


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /MOD/
      DOUBLE PRECISION::TOLD(nMaxUnits)=0.  !REVISIT: this variable is not used anywhere.
      DOUBLE PRECISION::DTOLD(nMaxUnits)=0.


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /NEWIO/
      INTEGER::PTRT(nMaxDerivatives)=0
      INTEGER::INPMAP(nMaxUnits*10,2)=0
	DOUBLE PRECISION::XT(nMaxUnits*10)=0.
	INTEGER::NDER(nMaxDerivatives)=0
      INTEGER::NUMDR


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /NEWUNT/
C  these variables are used by SOLVER 1 to determine new number of units in the 
C   trnsys deck after "deleting" all unused components 
      INTEGER::NEWNUM           !the new number of units
      INTEGER::UNMOD(nMaxUnits)=0  !array of old (pre modification) UNIT numbers
      INTEGER::NEWMAP(nMaxUnits,2)=0 !array of new (post modification) UNIT numbers


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /POWELL/
      DOUBLE PRECISION::ACC=0.0001    !
	DOUBLE PRECISION::PWSTEP=0.0001 !step for the new jacobian solver calculation
	INTEGER::MAXFUN=100             !max step in the iteration
	DOUBLE PRECISION::DMAX=100000.  !max # of function calls in the iteration


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /PRT1/
      DOUBLE PRECISION::OUT(nMaxOutputs) !outputs from all units (stored sequentially)
	INTEGER::IOUTPT(nMaxUnits) !pointer which locates the first storage space 
	                        !in OUT for unit IU
	DATA OUT/nMaxOutputs*0./,IOUTPT/nMaxUnits*1/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /PTRN/
      INTEGER::NPOS=0  !total number of PARAMETERS used so far in 
	                 !simulation - effective length of PAR
      INTEGER::NUINP=0 !total number of INPUTS used so far in 
	                 !simulation - effective length of XIN
      INTEGER::NUOUT=0 !total number of OUTPUTS used so far in 
	                 !simulation - effective length of IOUT, INDEX and IUNIT
						 

C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /ROUT/ 
      INTEGER::IROUT=0 !is equal to zero for old solver and 1 or 2 for new solver
	INTEGER::ISYS=0  !1 is two backward and forward solutions are required
	INTEGER::JSYS=0  !current type of solution (1: forward, 0: backward)
	INTEGER::NEQ(2)  !number of equations in system
	                 !NEQ(1): forward
	                 !NEQ(2): backward
	LOGICAL :: ONLINE = .FALSE. !.TRUE. if online Type65 is present
      DATA NEQ/0,0/

! --- Solver 0 with numerical relaxation ---

      real(8) :: minRelaxFactor = 1.0d0
	real(8) :: maxRelaxFactor = 1.0d0
	logical :: isRelaxationOn = .false.
      real(8) :: outHistory(nMaxOutputs,2) = 0.0d0
      real(8) :: relaxFactor(nMaxOutputs) = 1.0d0


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /SIM/
      DOUBLE PRECISION :: TIME0 = 0.D0     !starting time of the simulation
	DOUBLE PRECISION :: TFINAL = 0.D0    !ending time of the simulation
	DOUBLE PRECISION :: DELT = 1.D0      !simulation timestep
	INTEGER*8        :: N_TIMESTEPS=0  	 !the number of timesteps to date
	INTEGER          :: IDENOM=1  	     !best fit of timestep in form INUMER/IDENOM
	INTEGER          :: INUMER=1  	     !best fit of timestep in form INUMER/IDENOM
	integer          :: nTimeSteps       ! Number of time steps in the simulation

C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /STRNGS/
      CHARACTER*1::HEADNG(maxFileWidth,10)=' ' !stores comments from the top of the simulaiton deck
	CHARACTER*1::BLANK      !character constants for the indicated symbol
	CHARACTER*1::COMMA      !character constants for the indicated symbol
	CHARACTER*1::MINUS      !character constants for the indicated symbol
	CHARACTER*1::PLUS       !character constants for the indicated symbol
	CHARACTER*1::MULT       !character constants for the indicated symbol
	CHARACTER*1::DIV        !character constants for the indicated symbol
	CHARACTER*1::E          !character constants for the indicated symbol
	CHARACTER*1::EQSIGN     !character constants for the indicated symbol
	CHARACTER*1::DECPT      !character constants for the indicated symbol
	CHARACTER*1::POWER      !character constants for the indicated symbol
	CHARACTER*1::DIGIT(10)  !array of characters 0 to 9
	CHARACTER*1::LETTER(26) !array of alphabetic characters (upper case)
	CHARACTER*1::LOWER(26)  !array of alphabetic characters (lower case)
	CHARACTER*1::OPERAT(10) !array of allowable operators for eqn processing
	CHARACTER*1::FUNC(29,6) !character representation of allowable functions 
	                        !for eqn processing
	CHARACTER*1::FUNCOP(29) !1 character representation of functions in func

      DATA MINUS/'-'/,PLUS/'+'/,DIV/'/'/,MULT/'*'/,POWER/'^'/,
     .         DECPT/'.'/,BLANK/' '/,EQSIGN/'='/,E/'E'/,COMMA/','/
      DATA DIGIT/'0','1','2','3','4','5','6','7','8','9'/
      DATA LETTER/'A','B','C','D','E','F','G','H','I','J',
     .    'K','L','M','N','O','P','Q','R','S','T','U','V',
     .    'W','X','Y','Z'/
      DATA LOWER/'a','b','c','d','e','f','g','h','i','j',
     .    'k','l','m','n','o','p','q','r','s','t','u','v',
     .    'w','x','y','z'/
      DATA OPERAT/'=',')','(','+','-','*','/','^','$',','/
      DATA FUNC
     & /'*','E','L','S','C','T','M','M','A','I','A','A','A','M','L','A',
     &      'O','N','G','L','E','G','L','N','A','G','E','N','G',

     &  '*','X','N','I','O','A','I','A','B','N','T','C','S','O','O','N',
     &      'R','O','T','T','Q','E','E','E','E','T','Q','E','E',

     &  ' ','P',' ','N','S','N','N','X','S','T','A','O','I','D','G','D',
     &      ' ','T',' ',' ','L',' ',' ',' ',' ','W','W','W','W',

     &  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','N','S','N',' ',' ',' ',
     &      ' ',' ',' ',' ',' ',' ',' ',' ',' ','A','A','A','A',

     &  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',
     &      ' ',' ',' ',' ',' ',' ',' ',' ',' ','R','R','R','R',

     &  ' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',
     &      ' ',' ',' ',' ',' ',' ',' ',' ',' ','N','N','N','N'/
      DATA FUNCOP/'^','e','l','s','c','t','x','n','a','p','r','z','v',
     &            'b','g','d','o','h','j','i','q','w','y','u','~','f',
     &            'k','m','%'/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /STRNG2/
      INTEGER::NOPER = 10
	INTEGER::NFUNC = 29
	INTEGER::PCODE(36) !polish notation for the operators and functions

C.    FIRST PCODES ARE FOR THE OPERATOR ARRAY; SECOND AND THIRD ROW FOR FUNCTIONS
	DATA PCODE/3,4,1,2,5,6,10,
     & 5,14,13,15,16,21,12,11,20,8,19,18,17,9,22,23,24,7,25,26,27,28,29,
     & 30,31,32,33,34,35/

C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /SYSMAP/
      !these variables store information about the the system of algebraic 
      !equations to be solved by SOLVER 1. 
      INTEGER::PEX(nMaxUnits,2)=0
	INTEGER::PEU(nMaxUnits,2)=0
	DOUBLE PRECISION::D(nMaxUnits)=0.


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /SYSTMX/ 
      CHARACTER*4::COMP !character variable set to 'main' for mainframe systems and 
                        !'micr' for microcomputers (IBM PC's, etc.). See also common
                        ! block /LUNITS/. With TRNSYS 14.0, COMP is read from CNFGTR.TRN


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /TRNERR/
      INTEGER*4::IERROR !TRNSYS error codes
      INTEGER*4::IWARN !TRNSYS error codes


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /TSAVE/
      DOUBLE PRECISION::TSTORE(nMaxDerivatives,3)
	DOUBLE PRECISION::DTSTOR(nMaxDerivatives)=0.
	DOUBLE PRECISION::SSTORE(nMaxStorageSpots)=0.

      DATA TSTORE/nMaxDerivative3*0./

C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /TYP65/
      DOUBLE PRECISION::PLOUT(20,5) !array contains plot values
	DOUBLE PRECISION::PROUT(20,5) !array contains plot parameters
	INTEGER::PLTNUM(5) !plot number
      CHARACTER*1::ONLAB(16,20,5) !array holding labels for online printing
	CHARACTER*1::ONTITL(50,3,5) !array contains plot titles
	CHARACTER*1::ONUNIT(6,2,5) !array contains plot label units

      DATA PLOUT/100*0.0/,PROUT/100*0.0/,PLTNUM/5*0/
      DATA ONLAB/1600*' '/,ONTITL/750*' '/,ONUNIT/60*' '/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /UNITS/
      INTEGER::NUNITS=nMaxUnits  !total number of units allowed in the simulation
      INTEGER::IUNITS=0.      !number of units specified in the user's deck
      INTEGER::IDECK(nMaxUnits)  !list of units specified in deck
      INTEGER::JUNITS=0.      !length of list in JCALL
      INTEGER::JCALL(nMaxUnits)  !list of units and loops. Loops are numbered sequentially and have 
    		                    !negative values
      INTEGER::NDEP(nMaxUnits)   !pointers into DTDT (indexed by unit number)
      INTEGER::NPAR(nMaxUnits)   !pointers into PAR (indexed by unit number)
      INTEGER::NPARAM=nMaxParameters   !total number of PARs allowed in a simulation
      DOUBLE PRECISION::PAR(nMaxParameters) !parameters for all units
      REAL::PAR_15(nMaxParameters)     !single precision parameters for all units
      INTEGER::INFO(15,nMaxUnits)     !info for the component subroutines (see manual)
      INTEGER::TRON(nMaxUnits)        !trace on time (indexed by unit number)
	INTEGER::TROFF(nMaxUnits)       !trace off time (indexed by unit number)
      DOUBLE PRECISION::ERTOL=0.001D0 !algebraic convergence tolerance
	DATA NPAR/nMaxUnits*0/
	DATA NDEP/nMaxUnits*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /UPDATE/
C  These structures allow EQUATIONS that depend upon OUTPUTS and INPUTS 
C   that depend upon EQUATIONS to be updated quickly.
      INTEGER::UPEPTR(nMaxUnits+1)   !points into UPDEQU.
      INTEGER::UPDEQU(nMaxEquations*20) !contains a list of EQUATIONS that must be updated when
                                  !OUTPUTS are changed. For a given UNIT, UPEPTR(UNIT)
                                  !points to the first EQUATION that needs to be changed
                                  !and UPEPTR(UNIT+1)-1 points to the last equation that needs to be changed. (NOTE
                                  !if (UPEPTR(UNIT)=UPEPTR(UNIT+1), there are no EQUATIONS to update.
      INTEGER::UPIPTR(nMaxEquations+1)  !points into UPDINP.
      INTEGER::UPDINP(2,nMaxEquations*2) !contains a list of INPUTS that must be updated when
                                   !EQUATIONS are changed. For a given INPUT, UPEPTR(EQN)
                                   !points to the first (UNIT,INPUT) that needs to be changed
                                   !and UPEPTR(EQN+1)-1 points to the last pair that needs to be changed. (NOTE
                                   !if (UPEPTR(EQN)=UPEPTR(EQN+1), there are no EQUATIONS to update.
      INTEGER::UPDEQU_TIME(nMaxEquations) !contains a list of EQUATIONS that must be updated when TIME is updated
	DATA UPDEQU_TIME/nMaxEquations*0/


C ********* VARIABLES PREVIOUSLY CONTAINED IN COMMON BLOCK /WARN/
C    The /WARN/ common block was only used in fluids.for. It is now declared there as well


C ********* VARIABLES NOT PREVIOUSLY CONTAINED IN COMMON BLOCKS
      DOUBLE PRECISION ERR_TIME !simulation time (set in trnsys.for)


C ********* VARIABLES FOR THE FILES OPENED BY TRNSYS
      INTEGER*4 :: OPENED_LU(nMaxFiles)		!INDICATOR FOR THE OPENED LOGICAL UNITS
      INTEGER*4 :: JSTORE_LU					!INDICATOR FOR THE NUMBER OF OPENED LOGICAL UNITS
	character (len=maxPathLength) :: opened_fName(nMaxFiles)    ! Array of strings with opened filenames

      DATA JSTORE_LU/0/,OPENED_LU/nMaxFiles*0/


C ********* VARIABLES FOR THE DESCRIPTIONS OF INPUTS FOR CERTAIN COMPONENTS - MAKE SURE TO SET THIS IF A NEW
C           COMPONENT REQUIRES INPUT DESCRIPTIONS
      LOGICAL DESCRIPS_OK(999)				    !INDICATES WHETHER A TYPE SUPPLIES INPUT DESCRIPTION (initialized in InitializeTrnsysData) 
	INTEGER N_DESCRIPS						!POINTER FOR NUMBER OF DESCRIPTIONS READ
	INTEGER DESCRIP_UNIT(nMaxDescriptions)	!THE UNIT NUMBER FOR THE CORRESPONDING DESCRIPTION
	CHARACTER*1 DESCRIP(maxDescripLength,nMaxDescriptions)	!THE ARRAY HOLDING THE DESCRIPTIONS
	
	DATA N_DESCRIPS/0/						!INITIALIZE TOTAL NUMBER OF VARIABLE DESCRIPTIONS FOUND
	DATA DESCRIP_UNIT/nMaxDescriptions*0/		!INITIALIZE ALL THE UNITS

C ********* VARIABLES FOR THE VARIABLE TYPES OF INPUTS FOR CERTAIN COMPONENTS - MAKE SURE TO SET THIS IF A NEW
C           COMPONENT REQUIRES INPUT VARIABLE TYPES 
      LOGICAL VARUNITS_OK(999)				    !INDICATES WHETHER A TYPE SUPPLIES VARIABLE TYPE INFORMATION  (initialized in InitializeTrnsysData) 
	INTEGER N_VARUNITS						!POINTER FOR NUMBER OF VARIABLE UNITS READ
	INTEGER VARUNIT_UNIT(nMaxVariableUnits)	!THE UNIT NUMBER FOR THE CORRESPONDING VARIABLE UNIT
      INTEGER CRITPAR_TYPE(999)				    !ARRAY HOLDING THE PARAMETER NUMBER WHICH INDICATES UNIT PRINTING  (initialized in InitializeTrnsysData) 
      INTEGER CRITPAR_VALUE(999)				!ARRAY HOLDING THE REQUIRED PARAMETER VALUE WHICH INDICATES UNIT PRINTING  (initialized in InitializeTrnsysData) 
	CHARACTER*1 VARUNIT(maxVarUnitLength,nMaxVariableUnits)	!THE ARRAY HOLDING THE VARIABLE UNITS

	DATA N_VARUNITS/0/						!INITIALIZE TOTAL NUMBER OF VARIABLE UNITS FOUND
	DATA VARUNIT_UNIT/nMaxVariableUnits*0/		!INITIALIZE ALL THE UNITS

C ********* VARIABLES FOR THE 'LABELS' CARD FOR COMPONENTS - MAKE SURE TO SET THIS IF A NEW
C           COMPONENT REQUIRES LABELS
      LOGICAL LABELS_OK(999)					!INDICATES WHETHER A TYPE REQUIRES LABELS (initialized in InitializeTrnsysData) 
	INTEGER N_LABELS						!POINTER FOR NUMBER OF LABELS READ SO FAR
	INTEGER LABEL_UNIT(nMaxLabels)		!THE UNIT NUMBER FOR THE CORRESPONDING LABEL
	CHARACTER*1 LABEL(maxLabelLength,nMaxLabels)		!THE ARRAY HOLDING THE LABELS
	
	DATA N_LABELS/0/						!INITIALIZE TOTAL NUMBER OF VARIABLE DESCRIPTIONS FOUND
	DATA LABEL_UNIT/nMaxLabels*0/			!INITIALIZE ALL THE UNITS
      DATA LABEL/nMaxLabelChars*' '/			!INITIALIZE ALL THE LABEL CHARACTERS

C ********* VARIABLES FOR THE 'FORMAT' CARD FOR COMPONENTS - MAKE SURE TO SET THIS IF A NEW
C           COMPONENT REQUIRES FORMATS
      LOGICAL FORMATS_OK(999)							!INDICATES WHETHER A TYPE ALLOWS FORMAT STATEMENTS (initialized in InitializeTrnsysData)
	INTEGER N_FORMATS								!POINTER FOR NUMBER OF FORMATS READ SO FAR
	INTEGER FORMAT_UNIT(nMaxFormats)				!THE UNIT NUMBER FOR THE CORRESPONDING FORMAT
	CHARACTER(len=maxFileWidth) FORMAT_LINE(nMaxFormats)		!THE ARRAY HOLDING THE FORMATS
	
	DATA N_FORMATS/0/								!INITIALIZE TOTAL NUMBER OF FORMAT STATEMENTS FOUND
	DATA FORMAT_UNIT/nMaxFormats*0/				!INITIALIZE ALL THE UNITS

C ********* VARIABLES FOR THE 'CHECK' CARD FOR COMPONENTS - MAKE SURE TO SET THIS IF A NEW
C           COMPONENT REQUIRES CHECKS
      LOGICAL CHECKS_OK(999)									!INDICATES WHETHER A TYPE ALLOWS CHECK STATEMENTS (initialized in InitializeTrnsysData)
	INTEGER N_CHECKS										!POINTER FOR NUMBER OF CHECK STATEMENTS READ SO FAR
	INTEGER CHECK_UNIT(nMaxChecks)						!THE UNIT NUMBER FOR THE CORRESPONDING CHECK STATEMENT
	INTEGER CHECK_CODES(nMaxCheckCodes,nMaxChecks)		!THE CODES FROM THE CHECK STATEMENT
	DOUBLE PRECISION CHECK_TOL(nMaxChecks)						!THE TOLERANCES FOR THE CHECK STATMENT
      DOUBLE PRECISION CHK_SUM_MAX(nMaxChecks)				!MAXIMUM VALUE OF CHECK STATEMENT RESULT OVER THE SIMULATION
	DATA N_CHECKS/0/										!INITIALIZE TOTAL NUMBER OF CHECK STATEMENTS FOUND
	DATA CHECK_UNIT/nMaxChecks*0/							!INITIALIZE ALL THE UNITS
	DATA CHK_SUM_MAX/nMaxChecks*0.D0/							!INITIALIZE ALL THE UNITS

C ********* VARIABLE FOR THE TIME SPENT IN THE TYPES
	DOUBLE PRECISION :: TIME_SPENT_UNIT(nMaxUnits)=0.0d0, 
     .                    TIME_SPENT_TYPE(999)=0.0d0

C ********* ARRAY FOR NUMBER OF STORAGE VARIABLES FOR EACH UNIT
      INTEGER :: ISTORE_UNIT(nMaxUnits,2)=0      
      INTEGER :: StaticISTORE_UNIT(nMaxUnits,2)=0      
	INTEGER :: DynamicISTORE_UNIT(nMaxUnits,2)=0
	INTEGER :: StorageLocation(nMaxUnits)=0

C ********* ARRAY WHICH HOLDS THE VERSION INFORMATION FOR EACH TYPE
      LOGICAL::VERSION_15(nMaxUnits)   
      DATA VERSION_15/nMaxUnits*.FALSE./

C ********* ARRAY WHICH HOLDS THE TOTAL NUMBER OF ITERATIVE CALLS FOR EACH TYPE
      INTEGER::I_CALLS(nMaxUnits)   
      DATA I_CALLS/nMaxUnits*0/

C ********* ARRAY WHICH INDICATES WHICH EQUATIONS SHOULD BE UPDATED
      LOGICAL::CALL_EQN(nMaxEquations)   
      DATA CALL_EQN/nMaxEquations*.FALSE./

C ********* VARIABLE WHICH INDICATES HOW EQUATIONS SHOULD BE UPDATED
      INTEGER::I_EQSOLVER   
      DATA I_EQSOLVER/0/

C ********* VARIABLE THAT INDICATES WHETHER POINTERS TO TYPE LOCATIONS HAVE BEEN VERIFIED
      LOGICAL::CheckedLinks   
      DATA CheckedLinks/.FALSE./

C ********* VARIABLES WHICH INDICATES WHEN EQUATIONS SHOULD BE TRACED
      DOUBLE PRECISION ETRON,ETROFF   
	LOGICAL EQN_TRACE
      DATA ETRON/-99.D0/,ETROFF/-99.D0/,EQN_TRACE/.FALSE./

C ********* VARIABLES WHICH INDICATES WHICH EQUATIONS SHOULD BE UPDATED WHEN ANOTHER
C           EQUATION IS CHANGED
      INTEGER N_UPDVARS(nMaxEquations,2),UPDVARS(nMaxEquations*10)
	DATA N_UPDVARS/nMaxEquations2*0/,UPDVARS/nMaxEquations10*0/

C ********* VARIABLES WHICH INDICATES THE TRNSYS INPUT FILE VERSION
      INTEGER VERSNUM,MINORVERSNUM
	DATA VERSNUM/0/,MINORVERSNUM/0/

C *********
	double precision time0V15   ! Used to keep track of the original simulation start time in a Version 15 deck
	data time0V15/-9999.0d0/ 

C ********* THE MAXIMUM FLOATING POINT VALUE FOR OUTPUTS FROM A TRNSYS COMPONENT
      DOUBLE PRECISION BIG_NUMBER
	DATA BIG_NUMBER/1.E+38/

C ********* VARIABLE FOR SOLVER STABILITY
	LOGICAL STABLE
	DATA STABLE/.TRUE./

C ********* VARIABLE FOR THE PROGRESS BAR
      INTEGER IPROGRESS
	DATA IPROGRESS/1/

C ********* VARIABLES FOR THE CONVERSION FACTORS BETWEEN UNITS
      DOUBLE PRECISION XI(nMaxUnitConversions),AI(nMaxUnitConversions)


C ********* VARIABLES THAT WERE IN THE COMMON BLOCK /DFEQ/
C     EPSILN      DIFFERENTIAL EQUATION CONVERGENCE TOLERANCE
C     NDERIV      NUMBER OF DERIVATIVES IN THE SIMULATION--HAS MAXIMUM VALUE
C                 FROM PARAM.INC AND IS THEN RESET TO ACTUAL NUMBER IN PROC
C     DFQTYP      INDICATES METHOD USED FOR SOLVING THE DIFFERENTIAL EQNS
C                 1    MODIFIED EULER METHOD
C                 2    HEUN'S METHOD
C                 3    ADAM'S-BASHFORTH METHOD
C     DFQERR      LIST OF DIFFERENTIAL EQUATIONS WHICH HAVE NOT CONVERGED
C     DTDT        DERIVATIVE ARRAY
C     T           STORES THREE COPIES (PREDICTED, CORRECTED AND LAST VALUE) OF THE TIME DEPENDENT VARIABLES.

      INTEGER NDERIV,DFQTYP,DFQERR(nMaxDerivatives),LAST
	DOUBLE PRECISION EPSILN,DTDT(nMaxDerivatives),T(nMaxDerivatives,3)
	DATA NDERIV/nMaxDerivatives/,DFQTYP/1/,EPSILN/.001D0/,LAST/1/,
     &     DTDT/nMaxDerivatives*0./,T/nMaxDerivative3*0./

C ********* VARIABLES TO CHECK IF THE OUTPUTS FROM A UNIT ARE BEING CALCULATED AS "NOT A NUMBER" AND TO SEE
C           IF THE OUTPUTS ARE BEING WRITTEN OUTSIDE OF THEIR ALLOTED SPOT IN THE GLOBAL OUTPUT ARRAY
      LOGICAL CHECK_NAN,CHECK_OVERWRITE
	DATA CHECK_NAN/.FALSE./,CHECK_OVERWRITE/.FALSE./

C ********* VARIABLES TO CHECK IF THE TIME REPORTS ARE TURNED ON OR OFF
      LOGICAL TIME_REPORT
	DATA    TIME_REPORT /.FALSE./ 

C ********* VARIABLES AND DATA STRUCTURES FOR THE DEMO VERSION


	integer, parameter :: nUnitsAllowedInDemo =        5  ! Maximum number of types allowed in demo version

	integer, parameter :: nExamples			  =       17  ! Number of approved examples for demo vesion

	integer, parameter :: maxExampleTypes     =       12  ! Maximum mumber of types in examples for demo version


	TYPE ExampleInfo
	  CHARACTER (len=maxPathLength) :: ExDeckName
	  INTEGER :: ExTypes(maxExampleTypes)
	  INTEGER :: ExUnits
	ENDTYPE ExampleInfo

	TYPE(ExampleInfo) :: Example(nExamples)

      DATA Example(1)%ExDeckName/'Begin.dck'/
	DATA Example(1)%ExTypes/1,3,6,14,24,25,65,109,0,0,0,0/
	DATA Example(1)%ExUnits/8/
	DATA Example(2)%ExDeckName/'Diesel Dispatch.dck'/
	DATA Example(2)%ExTypes/14,25,65,102,120,0,0,0,0,0,0,0/
	DATA Example(2)%ExUnits/6/
	DATA Example(3)%ExDeckName/'Electrolyzer controller.dck'/
	DATA Example(3)%ExTypes/8,57,65,100,109,160,164,175,180,0,0,0/
      DATA Example(3)%ExUnits/6/
	DATA Example(4)%ExDeckName/'SDHW - Feedback controller.dck'/
	DATA Example(4)%ExTypes/1,4,11,14,22,24,25,65,109,110,0,0/
	DATA Example(4)%ExUnits/14/
	DATA Example(5)%ExDeckName/'Simple zone - Feedback controller.
     &dck'/
	DATA Example(5)%ExTypes/14,22,28,65,88,93,109,0,0,0,0,0/
	DATA Example(5)%ExUnits/9/
	DATA Example(6)%ExDeckName/'Simple zone - PID controller.dck'/
	DATA Example(6)%ExTypes/14,23,28,65,88,93,109,0,0,0,0,0/
	DATA Example(6)%ExUnits/9/
	DATA Example(7)%ExDeckName/'SunSpace - Floor heating PID controlle
     &r.dck'/
	DATA Example(7)%ExTypes/14,23,33,56,57,65,69,109,0,0,0,0/
	DATA Example(7)%ExUnits/9/
	DATA Example(8)%ExDeckName/'Restaurant.dck'/  !This version has only 2 instances of Type28
	DATA Example(8)%ExTypes/28,33,56,65,69,109,0,0,0,0,0,0/
	DATA Example(8)%ExUnits/7/
	DATA Example(9)%ExDeckName/'SDHW.dck'/
	DATA Example(9)%ExTypes/1,2,3,4,11,14,24,25,65,109,0,0/
	DATA Example(9)%ExUnits/14/
	DATA Example(10)%ExDeckName/'ShadingMasks.dck'/
	DATA Example(10)%ExTypes/28,65,68,71,109,0,0,0,0,0,0,0/
	DATA Example(10)%ExUnits/6/
	DATA Example(11)%ExDeckName/'Stand-Alone Power System.dck'/
	DATA Example(11)%ExTypes/9,14,25,28,65,90,105,120,160,164,173,175/
	DATA Example(11)%ExUnits/15/
	DATA Example(12)%ExDeckName/'SunSpace.dck'/
	DATA Example(12)%ExTypes/33,56,57,65,69,109,0,0,0,0,0,0/
	DATA Example(12)%ExUnits/6/
	DATA Example(13)%ExDeckName/'Type109.dck'/
	DATA Example(13)%ExTypes/65,109,0,0,0,0,0,0,0,0,0,0/
	DATA Example(13)%ExUnits/5/
	DATA Example(14)%ExDeckName/'Wind Diesel.dck'/
	DATA Example(14)%ExTypes/9,14,25,65,90,102,120,0,0,0,0,0/
	DATA Example(14)%ExUnits/10/
	DATA Example(15)%ExDeckName/'PID-Cooling-Flowrate.dck'/
	DATA Example(15)%ExTypes/4,23,65,0,0,0,0,0,0,0,0,0/
	DATA Example(15)%ExUnits/3/
	DATA Example(16)%ExDeckName/'PID-Cooling-Power.dck'/
	DATA Example(16)%ExTypes/23,65,88,0,0,0,0,0,0,0,0,0/
	DATA Example(16)%ExUnits/3/
	DATA Example(17)%ExDeckName/'rest_com.dck'/
	DATA Example(17)%ExTypes/14,25,28,33,56,65,69,109,157,0,0,0/
	DATA Example(17)%ExUnits/10/


	END MODULE TrnsysData


      subroutine InitializeTrnsysData()
      
      use TrnsysData
      
      implicit none
      
      ! Initialize DESCRIPS_OK
      DESCRIPS_OK      = .false.    ! Default: no descriptors
      DESCRIPS_OK( 25) = .true.     ! Type  25 has desriptors and not initial values
      DESCRIPS_OK( 26) = .true.     ! Type  26 has desriptors and not initial values
      DESCRIPS_OK( 27) = .true.     ! Type  27 has desriptors and not initial values
!      DESCRIPS_OK( 28) = .true.     ! Type  28 has desriptors and not initial values #Rev#MKu# not really!
      DESCRIPS_OK( 65) = .true.     ! Type  65 has desriptors and not initial values
      DESCRIPS_OK(535) = .true.     ! Type 535 has desriptors and not initial values
      DESCRIPS_OK(580) = .true.     ! Type 580 has desriptors and not initial values
      
      ! Initialize variables related to input variable types (units)
      VARUNITS_OK        = .false.  ! Default: no input variable types (units)
      CRITPAR_TYPE       = 0
      CRITPAR_VALUE      = -99
      VARUNITS_OK( 25)   = .true.   ! Type  25 has input variable types (units) if parameter( 5) = 1
      CRITPAR_TYPE( 25)  = 5
      CRITPAR_VALUE( 25) = 1
      VARUNITS_OK( 65)   = .true.   ! Type  65 has input variable types (units) if parameter(11) = 1
      CRITPAR_TYPE( 65)  = 11
      CRITPAR_VALUE( 65) = 1
      VARUNITS_OK(535)   = .true.   ! Type 535 has input variable types (units) if parameter( 2) = 1
      CRITPAR_TYPE(535)  = 2
      CRITPAR_VALUE(535) = 1
      VARUNITS_OK(580)   = .true.   ! Type 580 has input variable types (units) if parameter(11) = 1
      CRITPAR_TYPE(580)  = 11       ! #MKuTEMP# REVISIT ... Check with TESS, this seems like copy paste mixture of Type 25 and 65
      CRITPAR_VALUE(580) = 1

      ! Initialize variables related to labels
      LABELS_OK(  1:200) = .false.  ! Standard Types do not have labels except for the ones listed here below
      LABELS_OK( 25)     = .true.   ! Type  25 may have labels - used for EES lookup tables
      LABELS_OK( 28)     = .true.   ! Type  28 has labels
      LABELS_OK( 62)     = .true.   ! Type  62 has labels
      LABELS_OK(128)     = .true.   ! Type  128 has labels (TMP Type28)
      LABELS_OK(155)     = .true.   ! Type  155 has labels
      LABELS_OK( 65)     = .true.   ! Type  65 has labels
      LABELS_OK( 66)     = .true.   ! Type  66 has labels
	  LABELS_OK(101)     = .true.   ! Type  101 has labels
      LABELS_OK(128)     = .true.   ! Type  128 has labels (TMP Type28)
      LABELS_OK(155)     = .true.   ! Type  155 has labels
      LABELS_OK(201:999) = .true.   ! All user types CAN have labels
                   
      ! Initialize variables related to format statements
      FORMATS_OK      = .false. ! Default: no formats
      FORMATS_OK(  9) = .true.  ! Type   9 can have formats
      FORMATS_OK( 25) = .true.  ! Type  25 can have formats
      FORMATS_OK( 65) = .true.  ! Type  65 can have formats
      FORMATS_OK(535) = .true.  ! Type 535 can have formats
      FORMATS_OK(580) = .true.  ! Type 580 can have formats
      FORMATS_OK(657) = .true.  ! Type 657 can have formats
         
      ! Initialize variables related to check statements
      CHECKS_OK      = .true.     ! Default: Types CAN have check statements 
      CHECKS_OK(  2) = .false.    ! Type   2 cannot have check statements 
      CHECKS_OK(  9) = .false.    ! Type   9 cannot have check statements 
      CHECKS_OK( 14) = .false.    ! Type  14 cannot have check statements 
      CHECKS_OK( 25) = .false.    ! Type  25 cannot have check statements 
      CHECKS_OK( 65) = .false.    ! Type  65 cannot have check statements 
      CHECKS_OK( 89) = .false.    ! Type  89 cannot have check statements 
      CHECKS_OK(535) = .false.    ! Type 535 cannot have check statements 


      end subroutine InitializeTrnsysData
