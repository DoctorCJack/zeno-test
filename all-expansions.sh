#! /bin/bash

LB='\033[1;34m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

f=$1
# There are currently options 0-18
for e in {0..18}; do
	echo -e "Currently running ZENO on ${LB}${f}${NC} with expansion option ${ORANGE}${e}${NC}"
	bash runtests.sh $f $e;
done
