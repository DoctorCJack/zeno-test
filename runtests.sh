#! /bin/bash

source ./config.cfg

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
LB='\033[1;34m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

f=${1:-bods/unit-sphere.bod}
e=${2:-0}

numWalks=1000000

echo -e "${RED}CAUTION!${NC} Unless you know what you are doing, please do not run this in the background as it changes directories!"
pushd ${fp}/zeno-build/
make
popd

${fp}/zeno-build/zeno -i $f --num-walks=$numWalks --num-interior-samples=100000 --csv-output-file original-out.csv --expansion=0 > zeno-output.txt
${fp}/zeno-build/zeno -i $f --num-walks=$numWalks --num-interior-samples=100000 --csv-output-file modified-out.csv --expansion=$e >> zeno-output.txt

echo -e "${ORANGE}${numWalks} walks${NC}"
echo -e "${BLUE}Total number of steps taken by zeno-original:${NC}"
cat original-out.csv | grep steps
echo -e "${BLUE}Total number of steps taken by zeno-modified:${NC}"
cat modified-out.csv | grep steps
echo -e "${GREEN}Capacitance in original-out.csv:${NC}"
cat original-out.csv | grep capacitance,
echo -e "${GREEN}Capacitance in modified-out.csv:${NC}"
cat modified-out.csv | grep capacitance,

# [total-units, total-mean, total-std_dev, hit-units, hit-mean, hit-std_dev, miss-units, miss-mean, miss-std_dev]
originalArrSteps=($(grep "steps" original-out.csv | cut -d "," -f3-))
# [total-units, total-mean, total-std_dev, hit-units, hit-mean, hit-std_dev, miss-units, miss-mean, miss-std_dev]
modifiedArrSteps=($(grep "steps" modified-out.csv | cut -d "," -f3-))
# [units, mean, std_dev]
originalArrCapacitance=($(grep "capacitance" original-out.csv | cut -d "," -f3-))
# [units, mean, std_dev]
modifiedArrCapacitance=($(grep "capacitance" modified-out.csv | cut -d "," -f3-))

# Change numbers from scientific notation to standard notation
for i in {0..8}; do
  originalArrSteps[$i]=$(sed -E 's/([+-]?[0-9.]+)[eE]\+?(-?)([0-9]+)/(\1*10^\2\3)/g' <<< ${originalArrSteps[$i]});
  modifiedArrSteps[$i]=$(sed -E 's/([+-]?[0-9.]+)[eE]\+?(-?)([0-9]+)/(\1*10^\2\3)/g' <<< ${modifiedArrSteps[$i]});
done

# Change numbers from scientific notation to standard notation
for i in {0..2}; do
  originalArrCapacitance[$i]=$(sed -E 's/([+-]?[0-9.]+)[eE]\+?(-?)([0-9]+)/(\1*10^\2\3)/g' <<< ${originalArrCapacitance[$i]});
  modifiedArrCapacitance[$i]=$(sed -E 's/([+-]?[0-9.]+)[eE]\+?(-?)([0-9]+)/(\1*10^\2\3)/g' <<< ${modifiedArrCapacitance[$i]});
done

totalDiff=$(echo "scale=6; ${modifiedArrSteps[1]} - ${originalArrSteps[1]}" | bc)
hitDiff=$(echo "scale=6; ${modifiedArrSteps[4]} - ${originalArrSteps[4]}" | bc)
missDiff=$(echo "scale=6; ${modifiedArrSteps[7]} - ${originalArrSteps[7]}" | bc)
capacitanceDiff=$(echo "scale=6; ${modifiedArrCapacitance[1]} - ${originalArrCapacitance[1]}" | bc)

echo -e "${ORANGE}Expansion option ${e}${ORANGE}"
echo -e "${LB}zeno-modified${NC} has an average of ${YELLOW}${totalDiff}${NC} more ${BLUE}total steps${NC} than ${LB}zeno-original${NC}. (We want this number be as ${RED}negative${NC} as possible)"
echo -e "${LB}zeno-modified${NC} has an average of ${YELLOW}${hitDiff}${NC} more ${BLUE}hit steps${NC} than ${LB}zeno-original${NC}. (We want this number be as ${RED}negative${NC} as possible)"
echo -e "${LB}zeno-modified${NC} has an average of ${YELLOW}${missDiff}${NC} more ${BLUE}miss steps${NC} than ${LB}zeno-original${NC}. (We want this number be as ${RED}negative${NC} as possible)"
echo -e "${LB}zeno-modified${NC} has an average of ${YELLOW}${capacitanceDiff}${NC} more ${GREEN}capacitance${NC} than ${LB}zeno-original${NC}. (We want this number to be as ${RED}close to zero${NC} as possible)"

