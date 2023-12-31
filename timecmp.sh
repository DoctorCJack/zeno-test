#! /bin/bash

f=${1:-bods/unit-sphere.bod}
e=${2:-0}
printf "zeno-original time:"
time ~/zeno-original/zeno-build/zeno -i $f --num-walks=1000000 --num-interior-samples=100000 --csv-output-file /dev/null > /dev/null
printf "\nzeno-run-modified time:"
time ~/zeno-run-modified/zeno-build/zeno -i $f --num-walks=1000000 --num-interior-samples=100000 --csv-output-file /dev/null --expansion=$e > /dev/null
