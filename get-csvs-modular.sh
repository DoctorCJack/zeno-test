#! /bin/bash

source ./filepath.cfg

RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color
totalIters=${1:-1}

if [ ! -f ./checkpoint.csv ]; then
    echo -e "${ORANGE}File checkpoint.csv not found!${NC} Creating checkpoint file."
    firstBod=$(echo $(ls bods)[0] | cut -d. -f 1)
    echo -e "total,${totalIters}\niter,0\nbod,${firstBod}\nexpansion,0" > checkpoint.csv
else
    echo -e "${ORANGE}NOTICE!${NC} File checkpoint.csv already exists. The passed in parameter (if it exists) will be ignored."
fi
temp=($(grep "total" checkpoint.csv | cut -d "," -f2-))
if [ "$temp" != "" ]; then
    # if [ $totalIters != -1 ]; then
    #     echo -e "${RED}WARNING!${NC} A total number of iterations already exists in the checkpoint file. This value was chosen over the new input."
    # fi
    totalIters=$temp
fi
iter=($(grep "iter" checkpoint.csv | cut -d "," -f2-))
bod=($(grep "bod" checkpoint.csv | cut -d "," -f2-))
expansion=($(grep "expansion" checkpoint.csv | cut -d "," -f2-))
echo $totalIters
echo $iter
echo $bod
echo $expansion

# echo -e "${RED}CAUTION!${NC} Unless you know what you are doing, please do not run this in the background as it changes directories!"
# pushd ${fp}/zeno-build/
# make
# popd
