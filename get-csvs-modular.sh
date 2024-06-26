#! /bin/bash

source ./config.cfg

RED='\033[0;31m'
ORANGE='\033[0;33m'
LB='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ ! -f ./checkpoint.csv ]; then
    echo -e "${ORANGE}File checkpoint.csv not found!${NC} Creating checkpoint file."
    firstBod=$(echo $(ls bods)[0] | cut -d. -f 1)
    echo -e "iter,0\nbod,${firstBod}\nexpansion,0" > checkpoint.csv
else
    echo -e "${RED}CAUTION!${NC} If you want to restart the testing process, please delete checkpoint.csv."
fi

iter=($(grep "iter" checkpoint.csv | cut -d "," -f2-))
bod=($(grep "bod" checkpoint.csv | cut -d "," -f2-))
expansion=($(grep "expansion" checkpoint.csv | cut -d "," -f2-))

echo -e "${RED}CAUTION!${NC} Unless you know what you are doing, please do not run this in the background as it changes directories!"
pushd ${fp}/zeno-build/
make
popd

foundStart=false
firstIteration=true

for ((i=${iter}; i<${numIters}; i++)); do
    for b in $(ls bods); do
        b=$(echo $b | cut -d. -f 1)
        # Start at the bod specified in the checkpoint file.
        if [ $foundStart = false ]; then
            if [ $b = $bod ]; then
                foundStart=true
            else
                continue
            fi
        fi
        for ((e=0; e<=${numExpansions}; e++)); do
            # Start at the expansion specified in the checkpoint file.
            if [ $firstIteration = true ]; then
                e=$expansion
                firstIteration=false
            fi
            # This solution isn't ideal (as it may be a bit slower if a break happens around the generation of a control), but it works.
            if [ $e = 0 ]; then
                echo -e "Now creating ${LB}${i}-${b}-control.csv${NC}"
                ${fp}/zeno-build/zeno -i bods/${b}.bod --num-walks=10000000 --num-interior-samples=100000 --seed=$(($i + $numIters)) --csv-output-file csvs-modular/${i}-${b}-control.csv --expansion=0 > /dev/null;
            fi
            # Update the checkpoint file.
            echo -e "iter,${i}\nbod,${b}\nexpansion,${e}" > checkpoint.csv
            echo -e "Now creating ${LB}${i}-${b}-${e}.csv${NC}"
            ${fp}/zeno-build/zeno -i bods/${b}.bod --num-walks=10000000 --num-interior-samples=100000 --seed=${i} --csv-output-file csvs-modular/${i}-${b}-${e}.csv --expansion=$e > /dev/null;
        done
    done
done
echo -e "${GREEN}DONE!${NC}"