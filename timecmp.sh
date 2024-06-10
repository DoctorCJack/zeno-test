#! /bin/bash

# Deprecated

source ./filepath.cfg

f=${1:-bods/unit-sphere.bod}
e=${2:-0}
printf "zeno-original time:"
time ${fp}/zeno-build/zeno -i $f --num-walks=1000000 --num-interior-samples=100000 --csv-output-file /dev/null --expansion=0 > /dev/null
printf "\nzeno-modified time:"
time ${fp}/zeno-build/zeno -i $f --num-walks=1000000 --num-interior-samples=100000 --csv-output-file /dev/null --expansion=$e > /dev/null
