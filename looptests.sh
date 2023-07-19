#! /bin/bash

for ((i = 1; i <= $1; i++)); do bash runtests.sh; done
