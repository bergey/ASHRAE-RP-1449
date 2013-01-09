! TrnsysFunctions: Defines functions to access TRNSYS global constants and variables
! ----------------------------------------------------------------------------------------------------------------------
!
! This files defines all functions to access TRNSYS global constants and variables from user Types
!


! NOTE:
! The full dec$ lines like "dec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getLabel" and the "alias"
! directive (versus "dec$ attributes dllexport :: getLabel")
! are required if the functions are to be used in Fortran external DLL's compiled with other conventions for 
! external routines. This is the case for the current implementation of Type 62 for example
!
! Revision history
!  2005.07.15 - JWT: Added getIterationNumber()
!  2005.07.18 - DEB: Added getTrnsysDebugLibDir()
!  2005.11.02 - DAA: Added LOGICAL function getTimeReport()
!  2006.01.26 - DAA: Added functions that access INCON when Solver 1 is used
!  2006.08.28 - MKu: Added getNumberOfWarnings()
!  2006.09.01 - DEB/DAA : Added function getLUfileName
! ---------------------------------------------------------------------------------------------------------------------
!
!
! ----------------------------------------------------------------------------------------------------------------------
! Copyright © 2005 Solar Energy Laboratory, University of Wisconsin-Madison. All rights reserved.


module TrnsysFunctions 

implicit none ! Note: This statement applies to all functions after "contains"


contains


! ----------------------------------------------------------------------------------------------------------------------
! --- Access to global constants ---------------------------------------------------------------------------------------
! ----------------------------------------------------------------------------------------------------------------------


! maxDescripLength: Maximum length of a variable description, e.g. input descriptions for printers and plotters
function getMaxDescripLength()
    !dec$ attributes dllexport :: getMaxDescripLength
    use TrnsysConstants
    integer :: getMaxDescripLength
    getMaxDescripLength = maxDescripLength
end function getMaxDescripLength


! maxFileWidth: Maximum file width, i.e. maximum length of any line in any text file that must be read by TRNSYS
function getMaxFileWidth()
    !dec$ attributes dllexport :: getmaxFileWidth
    use TrnsysConstants
    integer :: getmaxFileWidth
    getmaxFileWidth = maxFileWidth
end function getmaxFileWidth


! maxLabelLength: Maximum length of labels
function getMaxLabelLength()
    !dec$ attributes dllexport :: getMaxLabelLength
    use TrnsysConstants
    integer :: getMaxLabelLength
    getMaxLabelLength = maxLabelLength
end function getMaxLabelLength


! maxPathLength: Maximum length of variables containing path- and filenames 
function getMaxPathLength()
    !dec$ attributes dllexport :: getMaxPathLength
    use TrnsysConstants
    integer :: getMaxPathLength
    getMaxPathLength = maxPathLength
end function getMaxPathLength


! nMaxStorageSpots: Number of Storage places in the S array
function getnMaxStorageSpots()
    !dec$ attributes dllexport :: getNMaxStorageSpots
    use TrnsysConstants
    integer :: getnMaxStorageSpots
    getnMaxStorageSpots = nMaxStorageSpots
end function getnMaxStorageSpots


! ----------------------------------------------------------------------------------------------------------------------
! --- Access to global variables ---------------------------------------------------------------------------------------
! ----------------------------------------------------------------------------------------------------------------------


function CheckStability()
    !dec$ attributes dllexport :: CheckStability
    use TrnsysData
    integer :: CheckStability
    if(STABLE) then
	   CheckStability=1
	else
	   CheckStability=0
	endif
end function CheckStability

function ErrorFound()
    !dec$ attributes dllexport :: ErrorFound
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: ErrorFound
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_ERRORFOUND", decorate :: ErrorFound
    use TrnsysData
    logical :: ErrorFound
        if(IERROR.gt.0) then
           ErrorFound = .true.
        else
       ErrorFound = .false.
        endif
end function ErrorFound 

function getConvergenceTolerance()
    !dec$ attributes dllexport :: getConvergenceTolerance
    use TrnsysData
    real(8) :: getConvergenceTolerance
    getConvergenceTolerance = ERTOL
end function getConvergenceTolerance

function getDeckFileName()
    !dec$ attributes dllexport :: getDeckFileName
    use TrnsysData
    character(len=maxPathLength) :: getDeckFileName
    getDeckFileName = trim(DECKN1)
end function getDeckFileName

function getFormat(i,j)   !i=unit #, j=format #
    !dec$ attributes dllexport :: getFormat
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m
    !character*maxFileWidth :: getFormat
    character (len=maxFileWidth) :: getFormat
    getFormat = '***'

    m=0
    do k=1,N_FORMATS
       if(FORMAT_UNIT(k).eq.i) then
          m=m+1
          if(m.eq.j) then
             getFormat=FORMAT_LINE(k)
          endif
       endif
    enddo
end function getFormat

function getLabel(i,j)   !i=unit #, j=label #
    !dec$ attributes dllexport :: getLabel
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getLabel
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETLABEL", decorate :: getLabel
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,n
    !character*maxLabelLength :: getLabel
    character (len=maxLabelLength) :: getLabel
    getLabel = 'Label not available'

	m=0
	do k=1,N_LABELS
	   if(LABEL_UNIT(k).eq.i) then
                m=m+1
		  if(m.eq.j) then
                     do n=1,maxLabelLength
                       getLabel(n:n)=LABEL(n,k)
		     enddo
		  endif
	   endif
	enddo
end function getLabel

function getListingFileLogicalUnit()
    !dec$ attributes dllexport :: getListingFileLogicalUnit
    use TrnsysData
    integer :: getListingFileLogicalUnit
    getListingFileLogicalUnit = LUW
end function getListingFileLogicalUnit

function getMinimumTimestep()
    !dec$ attributes dllexport :: getMinimumTimestep
    use TrnsysConstants
    real(8) :: getMinimumTimestep
    getMinimumTimestep = minTimeStep
end function getMinimumTimestep

function getNextAvailableLogicalUnit()
    !dec$ attributes dllexport :: getNextAvailableLogicalUnit
    use TrnsysData
    integer :: getNextAvailableLogicalUnit,LUnext,j

    LUnext=0
    do j=1,JSTORE_LU
       LUnext=max(LUnext,OPENED_LU(J))
    enddo
    LUnext=LUnext+1

    getNextAvailableLogicalUnit = LUnext

    JSTORE_LU=JSTORE_LU+1
    OPENED_LU(JSTORE_LU)=LUnext
end function getNextAvailableLogicalUnit

function getnMaxIterations()
    !dec$ attributes dllexport :: getnMaxIterations
    use TrnsysData
    integer :: getnMaxIterations
    getnMaxIterations = ITMAX
end function getnMaxIterations

function getnMaxWarnings()
    !dec$ attributes dllexport :: getnMaxWarnings
    use TrnsysData
    integer :: getnMaxWarnings
    getnMaxWarnings = IQTMAX
end function getnMaxWarnings

function getnTimeSteps()
    !dec$ attributes dllexport :: getnTimeSteps
    use TrnsysData
    integer :: getnTimeSteps
    getnTimeSteps = nTimeSteps
end function getnTimeSteps

function getNumberOfErrors()
    !dec$ attributes dllexport :: getNumberOfErrors
    use TrnsysData
    integer :: getNumberOfErrors
    getNumberOfErrors = IERROR
end function getNumberOfErrors

function getNumberOfWarnings()
    !dec$ attributes dllexport :: getNumberOfWarnings
    use TrnsysData
    integer :: getNumberOfWarnings
    getNumberOfWarnings = IWARN
end function getNumberOfWarnings

function getNumericalSolver()
    !dec$ attributes dllexport :: getNumericalSolver
    use TrnsysData
    integer :: getNumericalSolver
    getNumericalSolver = IROUT
end function getNumericalSolver

function getSimulationStartTime()
    !dec$ attributes dllexport :: getSimulationStartTime
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getSimulationStartTime
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETSIMULATIONSTARTTIME", decorate :: getSimulationStartTime
    use TrnsysData
    real(8) :: getSimulationStartTime
    getSimulationStartTime = TIME0
end function getSimulationStartTime

function getSimulationStartTimeV15()
    !dec$ attributes dllexport :: getSimulationStartTimeV15
    use TrnsysData
    real(8) :: getSimulationStartTimeV15
    getSimulationStartTimeV15 = time0V15
end function getSimulationStartTimeV15

function getSimulationStopTime()
    !dec$ attributes dllexport :: getSimulationStopTime
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getSimulationStopTime
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETSIMULATIONSTOPTIME", decorate :: getSimulationStopTime
    use TrnsysData
    real(8) :: getSimulationStopTime
    getSimulationStopTime = TFINAL
end function getSimulationStopTime

function getSimulationTimeStep()
    !dec$ attributes dllexport :: getSimulationTimeStep
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getSimulationTimeStep
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETSIMULATIONTIMESTEP", decorate :: getSimulationTimeStep
    use TrnsysData
    real(8) :: getSimulationTimeStep
    getSimulationTimeStep = DELT
end function getSimulationTimeStep

! function getTrnsysExeDir: returns the location of the file trnexe.exe.
function getTrnsysExeDir()
    !dec$ attributes dllexport :: getTrnsysExeDir
    use TrnsysData
    character (len=maxPathLength) :: getTrnsysExeDir
    getTrnsysExeDir = TrnsysExeDir
end function getTrnsysExeDir

! function getTrnsysInputFileDir: returns the location of the TRNSYS input file.
function getTrnsysInputFileDir()
    !dec$ attributes dllexport :: getTrnsysInputFileDir
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getTrnsysInputFileDir
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETTRNSYSINPUTFILEDIR", decorate :: getTrnsysInputFileDir
    use TrnsysData
    character (len=maxPathLength) :: getTrnsysInputFileDir
    getTrnsysInputFileDir = TrnsysInputFileDir
end function getTrnsysInputFileDir

function getTrnsysRootDir()
    !dec$ attributes dllexport :: getTrnsysRootDir
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getTrnsysRootDir
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETTRNSYSROOTDIR", decorate :: getTrnsysRootDir
    use TrnsysData
    character (len=maxPathLength) :: getTrnsysRootDir
    getTrnsysRootDir = TrnsysRootDir
end function getTrnsysRootDir

! function getTrnsysUserLibDir: returns the location of the directory that contains Release versions of external DLLs.
function getTrnsysUserLibDir()
    !dec$ attributes dllexport :: getTrnsysUserLibDir
    use TrnsysData
    character (len=maxPathLength) :: getTrnsysUserLibDir
    getTrnsysUserLibDir = TrnsysUserLibDir
end function getTrnsysUserLibDir

! function getTrnsysUserLibDir: returns the location of the directory that contains Debug versions of external DLLs.
function getTrnsysDebugLibDir()
    !dec$ attributes dllexport :: getTrnsysDebugLibDir
    use TrnsysData
    character (len=maxPathLength) :: getTrnsysDebugLibDir
    getTrnsysDebugLibDir = TrnsysDebugLibDir
end function getTrnsysDebugLibDir

! double precision function returns the TRNSYS input file's major version number (XX in XX.y)
function getVersionNumber()
    !dec$ attributes dllexport :: getVersionNumber
    use TrnsysData
    integer :: getVersionNumber
    getVersionNumber = VERSNUM
end function getVersionNumber

! double precision function returns the TRNSYS input file's minor version number (y in XX.y)
function getMinorVersionNumber()
    !dec$ attributes dllexport :: getMinorVersionNumber
    use TrnsysData
    integer :: getMinorVersionNumber
    getMinorVersionNumber = MINORVERSNUM
end function getMinorVersionNumber

function LogicalUnitIsOpen(i)   !i=logical unit #
    !dec$ attributes dllexport :: LogicalUnitIsOpen
    use TrnsysData
    integer :: LUnext,i,j
	logical :: LogicalUnitIsOpen

    LogicalUnitIsOpen=.false.
    do j=1,JSTORE_LU
       if(OPENED_LU(J).eq.i) LogicalUnitIsOpen=.true.
    enddo
end function LogicalUnitIsOpen

function getVariableDescription(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getVariableDescription
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,n
	character (len=maxDescripLength) :: getVariableDescription
    getVariableDescription = 'Not available'

	m=0
	do k=1,N_DESCRIPS
	   if(DESCRIP_UNIT(k).eq.i) then
          m=m+1
		  if(m.eq.j) then
             do n=1,maxDescripLength
                getVariableDescription(n:n)=DESCRIP(n,k)
		     enddo
		  endif
	   endif
	enddo
end function getVariableDescription

function getVariableUnits(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getVariableUnits
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,n
	character (len=maxVarUnitLength) :: getVariableUnits
    getVariableUnits = 'Unknown'

	m=0
	do k=1,N_VARUNITS
	   if(VARUNIT_UNIT(k).eq.i) then
          m=m+1
		  if(m.eq.j) then
             do n=1,maxVarUnitLength
                getVariableUnits(n:n)=VARUNIT(n,k)
		     enddo
		  endif
	   endif
	enddo
end function getVariableUnits


! getTimeReport: Returns the current value of TIME_REPORT
function getTimeReport()
    !dec$ attributes dllexport :: getTimeReport
    !d!ec$ attributes dllexport, c, reference, nomixed_str_len_arg :: getTimeReport
    !d!ec$ attributes alias:"TRNSYSFUNCTIONS_mp_GETTIMEREPORT", decorate :: getTimeReport
    use TrnsysData
    logical :: getTimeReport
    getTimeReport = TIME_REPORT
end function getTimeReport 

! getLUFileName: Returns the name of the file corresponding to the logical unit number i
function getLUFileName(i)
        !dec$ attributes dllexport :: getLUFileName
        use TrnsysData
        character(len=maxPathLength) :: getLUFileName
        integer :: i,j
        getLUFileName = 'cannot find a file associated with that logical unit'
        do j=1,size(opened_lu)
          if (opened_lu(j)==i) then
                    getLUFileName = trim(opened_fName(j))
                    exit
          endif
        enddo
end function getLUFileName 

! ----------------------------------------------------------------------------------------------------------------------
! --- Additional access functions for kernel routines ------------------------------------------------------------------
! ----------------------------------------------------------------------------------------------------------------------

function getConnectedOutputNumber(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedOutputNumber
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,getConnectedOutputNumber

	k=INP(i)-1+j
    getConnectedOutputNumber=INCON(k,2)

end function getConnectedOutputNumber

function getConnectedUnitNumber(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedUnitNumber
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,getConnectedUnitNumber

	k=INP(i)-1+j
    getConnectedUnitNumber=INCON(k,1)

end function getConnectedUnitNumber

function getConnectedTypeNumber(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedTypeNumber
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,getConnectedTypeNumber

	k=INP(i)-1+j
    m=INCON(k,1)
	getConnectedTypeNumber=INFO(2,m)

end function getConnectedTypeNumber

function getConnectedVariableType(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedVariableType
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,outu,outno
	character*3 :: getConnectedVariableType

	k=INP(i)-1+j

    outu=INCON(k,1)
    outno=INCON(k,2)

    if((outno.LT.0).OR.(outu.EQ.0).OR.(outno.EQ.0)) THEN
       getConnectedVariableType='NAV'
    else
       m=IOUTPT(outu)+outno-1
       getConnectedVariableType=OCHECK(m)
    endif

end function getConnectedVariableType

function getConnectedVariableUnit(i,j)  !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedVariableUnit
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,n,outu,outno
	character*3 :: TRUTYP
	character (len=maxVarUnitLength) :: getConnectedVariableUnit

	k=INP(i)-1+j

    outu=INCON(k,1)
    outno=INCON(k,2)

    if((outno.LT.0).OR.(outu.EQ.0).OR.(outno.EQ.0)) then
       TRUTYP='NAV'
    else
       m=IOUTPT(outu)+outno-1
       TRUTYP=OCHECK(m)
    endif

    do n=1,nMaxUnitConversions
	   if(TRUTYP.EQ.CHTYP1(n)) then
	      getConnectedVariableUnit=CHTYP2(n)
	   endif
	enddo

end function getConnectedVariableUnit

! getIterationNumber: Returns the current INFO(8) iteration counter for a supplied UNIT
function getIterationNumber(i)
    !dec$ attributes dllexport :: getIterationNumber 
    use TrnsysData
    use TrnsysConstants
    integer :: i,getIterationNumber
    if ((i > 0).and.(i <= nMaxUnits)) then
      getIterationNumber = INFO(8,i)
	else
	  getIterationNumber = -1
	endif

end function getIterationNumber


! --- Additional access functions for kernel routines with Solver 1---------------------------------------------------

function getConnectedOutputNumberS1(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedOutputNumberS1
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,getConnectedOutputNumberS1

	k=INP(i)-1+j
    getConnectedOutputNumberS1=INCON_ORIG(k,2)

end function getConnectedOutputNumberS1

function getConnectedUnitNumberS1(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedUnitNumberS1
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,getConnectedUnitNumberS1

	k=INP(i)-1+j
    getConnectedUnitNumberS1=INCON_ORIG(k,1)

end function getConnectedUnitNumberS1

function getConnectedTypeNumberS1(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedTypeNumberS1
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,getConnectedTypeNumberS1

	k=INP(i)-1+j
    m=INCON_ORIG(k,1)
	getConnectedTypeNumberS1=INFO(2,m)

end function getConnectedTypeNumberS1

function getConnectedVariableTypeS1(i,j)   !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedVariableTypeS1
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,outu,outno
	character*3 :: getConnectedVariableTypeS1

	k=INP(i)-1+j

    outu=INCON_ORIG(k,1)
    outno=INCON_ORIG(k,2)

    if((outno.LT.0).OR.(outu.EQ.0).OR.(outno.EQ.0)) THEN
       getConnectedVariableTypeS1='NAV'
    else
       m=IOUTPT(outu)+outno-1
       getConnectedVariableTypeS1=OCHECK(m)
    endif

end function getConnectedVariableTypeS1

function getConnectedVariableUnitS1(i,j)  !i=unit #, j=input #
    !dec$ attributes dllexport :: getConnectedVariableUnitS1
    use TrnsysData
    use TrnsysConstants
    integer :: i,j,k,m,n,outu,outno
	character*3 :: TRUTYP
	character (len=maxVarUnitLength) :: getConnectedVariableUnitS1

	k=INP(i)-1+j

    outu=INCON_ORIG(k,1)
    outno=INCON_ORIG(k,2)

    if((outno.LT.0).OR.(outu.EQ.0).OR.(outno.EQ.0)) then
       TRUTYP='NAV'
    else
       m=IOUTPT(outu)+outno-1
       TRUTYP=OCHECK(m)
    endif

    do n=1,nMaxUnitConversions
	   if(TRUTYP.EQ.CHTYP1(n)) then
	      getConnectedVariableUnitS1=CHTYP2(n)
	   endif
	enddo

end function getConnectedVariableUnitS1




















end module TrnsysFunctions



















! ----------------------------------------------------------------------------------------------------------------------
! --- Repeated functions for name decoration problem (Type62) ---
! #Rev#MKu#Tmp

!function getLabelT62(i,j)   !i=unit #, j=label #
!    !dec$ attributes dllexport :: getLabelT62
!    use TrnsysData
!    use TrnsysConstants
!    integer :: i,j,k,m,n
!   character*maxLabelLength :: getLabelT62
!    getLabelT62 = 'Label not available'
!
!   m=0
!   do k=1,N_LABELS
!      if(LABEL_UNIT(k).eq.i) then
!          m=m+1
!         if(m.eq.j) then
!             do n=1,maxLabelLength
!                getLabelT62(n:n)=LABEL(n,k)
!            enddo
!         endif
!      endif
!   enddo
!end function getLabelT62

!function getTrnsysInputFileDirT62()
!    !dec$ attributes dllexport :: getTrnsysInputFileDirT62
!    use TrnsysData
!    character (len=maxPathLength) :: getTrnsysInputFileDirT62
!    getTrnsysInputFileDirT62 = TrnsysInputFileDir
!end function getTrnsysInputFileDirT62

!function getSimulationStartTimeT62()
!    !dec$ attributes dllexport :: getSimulationStartTimeT62
!    use TrnsysData
!    real(8) :: getSimulationStartTimeT62
!    getSimulationStartTimeT62 = TIME0
!end function getSimulationStartTimeT62

!function getSimulationTimeStepT62()
!    !dec$ attributes dllexport :: getSimulationTimeStepT62
!    use TrnsysData
!    real(8) :: getSimulationTimeStepT62
!    getSimulationTimeStepT62 = DELT
!end function getSimulationTimeStepT62

