! TrnsysConstants: Defines TRNSYS global constants 
! ----------------------------------------------------------------------------------------------------------------------
!
! This files defines all global constants in TRNSYS
! It replaces param.inc
!
!
! ATTENTION
!
! - Only modify this file if you really have to. You should never set any global constant to a lower value than the 
!   TRNSYS 16 default
! - For backwards compatibility with TRNSYS 15 Types running in "Legacy mode", some constants are duplicated in 
!   .\SourceCode\Include\param.inc. That file should reflect all changes you make in TrnsysConstants.f90
!
! Revision history
! ---------------------------------------------------------------------------------------------------------------------
!
! ----------------------------------------------------------------------------------------------------------------------
! Copyright © 2005 Solar Energy Laboratory, University of Wisconsin-Madison. All rights reserved.


module TrnsysConstants 

!                     Constant Name                     Explanation                                    TRNSYS 16 Default
! ----------------------------------------------------------------------------------------------------------------------

integer, parameter :: nMaxUnits           =     1000  ! Maximum number of units                                     1000

integer, parameter :: nMaxEquations       =      500  ! Maximum number of equations                                  500

integer, parameter :: nMaxDerivatives     =      100  ! Maximum number of derivatives                                100

integer, parameter :: nMaxOutputs         =     3000  ! Maximum number of Outputs                                   3000

integer, parameter :: nMaxParameters      =     2000  ! Maximum number of Parameters                                2000

integer, parameter :: nMaxStorageSpots    =    10000  ! Number of Storage places in the S array                    10000

integer, parameter :: nStaticStorageSpots =    10000  ! Number of Storage places in the Static S array              5000

integer, parameter :: nMaxFiles           =      300  ! Maximum number of files that can be opened by TRNSYS         300

integer, parameter :: nMaxDescriptions    =      750  ! Maximum number of descriptions in an input file              750

integer, parameter :: nMaxVariableUnits   =      750  ! Maximum number of input variable types in an input file      750

integer, parameter :: nMaxLabels          =      100  ! Maximum number of labels in an input file                    100

integer, parameter :: nMaxFormats         =      100  ! Maximum number of format statements in an input file         100

integer, parameter :: nMaxChecks          =       20  ! Maximum number of chek statements in an input file            20

integer, parameter :: nMaxCheckCodes      =       30  ! Maximum number of outputs per CHECK statement                 30

integer, parameter :: nMaxUnitConversions =      250  ! Max. number of unit conversions allowed in units.lab file    250

integer, parameter :: nMaxUnitTypes       =      250  ! Maximum number of unit types allowed in units.lab file       250

integer, parameter :: nMaxCardValues      =      250  ! Max. nb. of values allowed in one TRNSYS input file card     250
                                                      ! E.g. a component with 500 parameters would require 
                                                      ! nMaxCardValues to be greater or equal to 500

real(8), parameter :: minTimeStep         =  0.1/3600 ! Minimum Simulation Time Step [in hours] (0.1 second)    0.1/3600

integer, parameter :: nMaxTimeSteps       =1000000000 ! Maximum number of time steps in a simulation (1 billion)    10^9

integer, parameter :: nMaxPlottedTimeSteps=    525601 ! Max. nb. of time steps plotted by the online plotter      525601
                                                      ! Note: This constant is set in TRNExe. Do not edit

integer, parameter :: nMaxErrorMessages   =      1000 ! Maximum number of standard error messages in TrnsysErrors   1000
                                                      ! Note: If you increase this constant, additional messages 
                                                      ! will not be initialized. Add lines in TrnsysErrors.f90


! Constants defining the length of strings in TRNSYS    Explanation                                    TRNSYS 16 Default
! ----------------------------------------------------------------------------------------------------------------------

integer, parameter :: maxPathLength      =       300  ! Maximum length of variables containing path- and filenames   300
                                                      ! Note: DFWIN defines MAX_PATH as 260 but Windows XP can 
                                                      ! actually use much longer pathnames
                                                      ! ATTENTION: TRNExe must be adapted if this constant is modified
                                                      !            Users should not change maxPathLength

integer, parameter :: maxFileWidth       =      1000  ! Maximum file width, i.e. maximum length of any line in a    1000
                                                      ! text file that must be read from / written to by TRNSYS
                                                      ! maxFileWidth should be >= maxPathLength
                                                      ! This constant is also used for strings, e.g. error messages

integer, parameter :: maxDescripLength   =        25  ! Maximum length of a variable description, e.g. input          25
                                                      ! descriptions for printers and plotters 
                                                      ! #Rev#MKu# Still hardcoded in most cases

integer, parameter :: maxVarUnitLength   =        20  ! Maximum length of units associated with variables             20
                                                      ! #Rev#MKu# Still hardcoded to 10 (also loop in Type25)

integer, parameter :: maxEqnNameLength   =        20  ! Maximum length of variable names in equations                 20

integer, parameter :: maxLabelLength     =       300  ! Maximum length of labels                                     300
                                                      ! Some labels are file- and pathnames so a suggested value is
                                                      ! maxLabelLength = maxPathLength

integer, parameter :: maxMessageLength   =       800  ! Maximum length of notices, warnings and error messages       800
                                                      ! Error messages and any text printed on the same line must 
                                                      ! fit within the maximum file width (maxFileWidth). 
                                                      ! It is recommended to set maxMessageLength to maxFileWidth-200

! Derived constants
! ----------------------------------------------------------------------------------------------------------------------

integer, parameter :: nMaxUnits2 = nMaxUnits*2, nMaxUnits10 = nMaxUnits*10, nMaxUnits20 = nMaxUnits*20
integer, parameter :: nMaxEquationsPls1 = nMaxEquations+1, nMaxEquations2 = nMaxEquations*2,    &
                      nMaxEquations10 = nMaxEquations*10
integer, parameter :: nMaxDerivative3 = nMaxDerivatives*3
integer, parameter :: nMaxLabelChars = nMaxLabels*maxLabelLength
integer, parameter :: nMaxConstantsInEquations = 3*nMaxEquations  ! Max. Nb. of constants in equations (NOT the maximum number of constants) 


end module TrnsysConstants