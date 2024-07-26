# zeno-test
Files used for testing [DoctorCJack/ZENO](https://github.com/DoctorCJack/ZENO) (formerly [mvk1-nist/ZENO](https://github.com/mvk1-nist/ZENO)).

## Setup instructions

- Follow the setup instructions for ZENO as seen [here](https://zeno.nist.gov/Compilation.html), but with the following changes:
  - Change every instance of `$HOME` to the directory assigned to `fp` in `config.cfg`. However, you should still use `$HOME` instead of `~`.
  - Run `git clone` on `https://github.com/DoctorCJack/ZENO.git` instead of `https://github.com/usnistgov/ZENO.git`.
- Run `git clone` on this repo into a separate directory (I usually have `zeno-modified` \[`fp` in `config.cfg`\] and `zeno-test` \[the directory that contains this entire repo\] both be in the same directory together).
- Change `config.cfg` to your preferences.
- You should now be good to go.

## Brief description of each file

### bods/*
The .bod files I used as input.

### all-expansions.sh
Runs `runtests.sh` on all expansion options for one bod file.

### compile-output.py
Takes in all the files from `csvs/` as input, compiles them together into one data structure, then formats that one data structure into a single file. After that, it makes graphs based on the data.

### config.cfg
Stores some constant variables shared across files.

### get-csvs.sh
Generates ZENO's csv output files for every combination of iteration, bod file, and expansion option and puts them into `csvs/`. Also generates an additional csv file for the combination of every iteration, every bod, and expansion option 0 to serve as a control.

### looptests.sh
Runs `runtests.sh` in a loop.

### runtests.sh
Runs one test comparison between the ZENO algorithm with no expansion option and one with a specific expansion option for one bod file. Prints a human-readable output.

### timecmp.sh
Compares the time difference between the unmodified ZENO algorithm and the ZENO algorithm with an expansion option as opposed to the step difference.
