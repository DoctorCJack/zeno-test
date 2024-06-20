#! /bin/bash

source ./config.cfg

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
    echo -e "${RED}CAUTION!${NC} If you want to restart the testing process, please delete checkpoint.csv."
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
# echo $totalIters
# echo $iter
# echo $bod
# echo $expansion

echo -e "${RED}CAUTION!${NC} Unless you know what you are doing, please do not run this in the background as it changes directories!"
pushd ${fp}/zeno-build/
make
popd

foundStart=false
firstIteration=true

for ((i=${iter}; i<${totalIters}; i++)); do
    # echo "i: " $i
    for b in $(ls bods); do
        b=$(echo $b | cut -d. -f 1)
        if [ $foundStart = false ]; then
            if [ $b = $bod ]; then
                foundStart=true
            else
                continue
            fi
        fi
        # echo "b: " $b
        for ((e=0; e<=${numExpansions}; e++)); do
            if [ $firstIteration = true ]; then
                e=$expansion
                firstIteration=false
            fi
            # echo "e: " $e
            # echo "i: " $i " b: " $b " e: " $e
            echo -e "total,${totalIters}\niter,${i}\nbod,${b}\nexpansion,${e}" > checkpoint.csv
            ${fp}/zeno-build/zeno -i bods/${b}.bod --num-walks=10000000 --num-interior-samples=100000 --seed=${i} --csv-output-file csvs-modular/${i}-${b}-${e}.csv --expansion=$e > /dev/null;
        done
    done
done