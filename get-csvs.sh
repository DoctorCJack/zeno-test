#! /bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}CAUTION!${NC} Unless you know what you are doing, please do not run this in the background as it changes directories!"
pushd ~/zeno-run-modified/zeno-build/
make
popd
for f in $(ls bods); do
	f=$(echo $f | cut -d. -f 1)
	~/zeno-run-modified/zeno-build/zeno -i bods/${f}.bod --num-walks=10000000 --num-interior-samples=100000 --csv-output-file csvs/original-${f}.csv --expansion=0 > /dev/null;
	for e in {0..18}; do
		~/zeno-run-modified/zeno-build/zeno -i bods/${f}.bod --num-walks=10000000 --num-interior-samples=100000 --csv-output-file csvs/modified-${f}-${e}.csv --expansion=$e > /dev/null;
	done;
done
