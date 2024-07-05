# zeno-test
Files used for testing [DoctorCJack/ZENO](https://github.com/DoctorCJack/ZENO) (formerly [mvk1-nist/ZENO](https://github.com/mvk1-nist/ZENO)).<br><br>
Example outputs can be found in `csvs/`, `out.csv`, and `out.txt`.

## Setup instructions

- Follow the setup instructions for ZENO as seen [here](https://zeno.nist.gov/Compilation.html), but with the following changes:
  - Change every instance of `$HOME` to the directory assigned to `fp` in `config.cfg`. However, you should still use `$HOME` instead of `~`.
  - Run `git clone` on `https://github.com/DoctorCJack/ZENO.git` instead of `https://github.com/usnistgov/ZENO.git`.
- Create a separate new directory and `git clone` this repo into it.
- Change `config.cfg` to your preferences.
- You should now be good to go.

## Brief description of each file

### bods/*
The .bod files I used as input.

### csvs/*
Sample .csv files generated by `get-csvs.sh`.

### all-expansions.sh
Runs `runtests.sh` on all expansion options for one bod file.

### compile-output-modular.py
Does the same thing as `compile-output.py`, but takes in files from `csvs-modular/` instead of `csvs/`, creates a separate `out.txt` and `out.csv` equivalent for each iteration and puts them into `outs/`. In addition to that, it averages the csvs in `outs/` into `out-modular.csv` and makes graphs based on the data in `out-modular.csv`.

### compile-output.py
Takes in all the files from `csvs/` as input, compiles them together into one data structure, then formats that one data structure into a human-readable output in `out.txt` and a computer-readable output in `out.csv`.

### config.cfg
Stores some constant variables shared across files.

### get-csvs-modular.sh
Does the same thing as `get-csvs.sh`, but now allows for stopping and continuing mid-run via a checkpoint file, can run for multiple iterations, deterministically chooses the seed for reproducibility, and puts the csv output files into `csvs-modular/` instead of `csvs/`.

### get-csvs.sh
Generates ZENO's csv output files for every combination of bod file and expansion option and puts them into `csvs/`. Also generates an additional csv file for the combination of every bod and expansion option 0 to serve as a control.

### looptests.sh
Runs `runtests.sh` in a loop.

### out.csv
Sample computer-readable file generated by `compile-output.py`.

### out.txt
Sample human-readable file generated by `compile-output.py`.

### runtests.sh
Runs one test comparison between the ZENO algorithm with no expansion option and one with a specific expansion option for one bod file. Prints a human-readable output.

### timecmp.sh
Compares the time difference between the unmodified ZENO algorithm and the ZENO algorithm with an expansion option as opposed to the step difference.
