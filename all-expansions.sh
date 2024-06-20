#! /bin/bash

source ./config.cfg

LB='\033[1;34m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

f=$1
for ((e=0; e<=${numExpansions}; e++)); do
	echo -e "Currently running ZENO on ${LB}${f}${NC} with expansion option ${ORANGE}${e}${NC}"
	bash runtests.sh $f $e;
done
