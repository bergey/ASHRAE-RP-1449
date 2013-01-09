TRNSYS_TYPE=152

G95 -fcase-upper -fno-underscoring -M TrnsysData.for 
G95 -fcase-upper -fno-underscoring -M TrnsysFunctions.f90 
G95 -fcase-upper -fno-underscoring -M TrnsysConstants.f90 

G95 -fcase-upper -fno-underscoring -c TrnsysFunctions.f90 
G95 -fcase-upper -fno-underscoring -c TrnsysData.for 
G95 -fcase-upper -fno-underscoring -c TrnsysConstants.f90 

G95 -fcase-upper -fno-underscoring -shared -mrtd -o Type${TRNSYS_TYPE}.dll Type${TRNSYS_TYPE}.for TrnsysConstants.o TrnsysFunctions.o TrnsysData.o -L. TRNDll.dll 
