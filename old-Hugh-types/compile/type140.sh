TRNSYS_TYPE=140

g95 -fcase-upper -fno-underscoring -M TrnsysData.for 
g95 -fcase-upper -fno-underscoring -M TrnsysFunctions.f90 
g95 -fcase-upper -fno-underscoring -M TrnsysConstants.f90 

echo "finished -M stage"

g95 -fcase-upper -fno-underscoring -c TrnsysFunctions.f90 
g95 -fcase-upper -fno-underscoring -c TrnsysData.for 
g95 -fcase-upper -fno-underscoring -c TrnsysConstants.f90 

g95 -ffixed-line-length-80 -fcase-upper -fno-underscoring -shared -mrtd -o Type${TRNSYS_TYPE}.dll Type${TRNSYS_TYPE}.for TrnsysConstants.o TrnsysFunctions.o TrnsysData.o -L. TRNDll.dll 
