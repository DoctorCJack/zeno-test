import re
import pandas as pd
import os

def num_from_df(df, name, type):
  result = list(df.loc[(df["name"] == name) & (df["type"] == type)]["value"])[0] # There should always be exactly one element in this list
  result = float(("%.8f" % float(result)).rstrip('0').rstrip('.')) # Converts a string in scientific notation to a float I can work with
  return result

# Get the number of expansions from config.cfg
with open("config.cfg", "r") as f:
  num_expansions = int(re.search("numExpansions=([0-9]+)", f.read()).groups()[0])

# Instantiate stuff
everything = dict(list()) # Dictionary where keys are bods and values are lists of dataframes
dir = "./csvs" # Where the input csvs are located
num_mods = 2 + num_expansions # The first 2 are zeno-original and the base case in zeno-modified
averages = [[0] * (num_mods - 1) for i in range(4)]

# Process the files and put all the necessary data into data structures
for filename in os.listdir(dir):
  csv = pd.read_csv(os.path.join(dir, filename))
  csv.columns = ["name", "type", "value"]
  # Matches on the filename to get the list ["modified", <bod filename>, <expansion option>]
  regex = re.search("^(modified)-(.*)-([0-9]+).csv$", filename)
  # If the filename didn't match, then match on the filename to get the list ["original", <bod filename>]
  if(regex == None):
    regex = re.search("^(original)-(.*).csv$", filename)
  g = regex.groups()
  # g[0] is "original" or "modified"
  # g[1] is the bod filename
  # g[2] is the expansion option
  if g[1] not in everything.keys():
    everything[g[1]] = list(range(num_mods))
  if g[0] == "modified":
    everything[g[1]][int(g[2]) + 1] = csv
  else:
    everything[g[1]][0] = csv

# Process the data structures created in the previous step and
# convert them into the contents of the output files
result = ("Each list here shows the difference of means between the original output and "
"the modified output measured in the original output's standard deviations.\n"
"If there is a * symbol next to one of the lists, that means that the standard deviation is less than 0.001 units.\n"
"Also, if the standard deviation is 0, it is set to 0.000001 to prevent dividing by 0.\n"
"The format for each element is <char><num>:<value> where the chars correspond as follows:\n"
"t - total_steps\nh - hit_steps\nm - miss_steps\nc - capacitance\n\n")
cols = [f"{c}{i}" for c in ['t', 'h', 'm', 'c'] for i in range(num_mods - 1)]
# `df` is used only for the .csv output and `result` is used only for the .txt output
# Both are worked on at the same time to prevent duplicate control flows
df = pd.DataFrame(columns = cols)
for bod in sorted(everything.keys()):
  df.loc[bod] = [0.0] * ((num_mods - 1) * 4)
  result += f"{bod}:\n    ["
  curr = everything[bod]
  og_df = curr[0]
  og_total_steps_mean = num_from_df(og_df, "total_steps", "value")
  og_total_steps_sd = num_from_df(og_df, "total_steps", "std_dev")
  og_hit_steps_mean = num_from_df(og_df, "hit_steps", "value")
  og_hit_steps_sd = num_from_df(og_df, "hit_steps", "std_dev")
  og_miss_steps_mean = num_from_df(og_df, "miss_steps", "value")
  og_miss_steps_sd = num_from_df(og_df, "miss_steps", "std_dev")
  og_capac_mean = num_from_df(og_df, "capacitance", "value")
  og_capac_sd = num_from_df(og_df, "capacitance", "std_dev")
  og_total_steps_sd = 0.000001 if og_total_steps_sd == 0 else og_total_steps_sd # To prevent a divide by zero error
  og_hit_steps_sd = 0.000001 if og_hit_steps_sd == 0 else og_hit_steps_sd # To prevent a divide by zero error
  og_miss_steps_sd = 0.000001 if og_miss_steps_sd == 0 else og_miss_steps_sd # To prevent a divide by zero error
  og_capac_sd = 0.000001 if og_capac_sd == 0 else og_capac_sd # To prevent a divide by zero error
  for i in range(1, num_mods):
    mod_df = curr[i]
    mod_total_steps_mean = num_from_df(mod_df, "total_steps", "value")
    mod_total_steps_sd = num_from_df(mod_df, "total_steps", "std_dev")
    # p-values ended up being unreliable since they were only returning a 1.0 or a 0.0 depending on if the mean was off by a millionth of a unit or not
    # As a replacement, I will be using the difference between means measured in standard deviations
    diff = (mod_total_steps_mean - og_total_steps_mean) / og_total_steps_sd
    result += f"t{i - 1}:{round(diff, 6)}; "
    averages[0][i - 1] += diff
    df.loc[bod, f"t{i - 1}"] = round(diff, 6)
  result += f"\b\b]{' *' if og_total_steps_sd < 0.001 else ''}\tmean:{og_total_steps_mean} sd:{og_total_steps_sd}\n    ["
  for i in range(1, num_mods):
    mod_df = curr[i]
    mod_hit_steps_mean = num_from_df(mod_df, "hit_steps", "value")
    mod_hit_steps_sd = num_from_df(mod_df, "hit_steps", "std_dev")
    diff = (mod_hit_steps_mean - og_hit_steps_mean) / og_hit_steps_sd
    result += f"h{i - 1}:{round(diff, 6)}; "
    averages[1][i - 1] += diff
    df.loc[bod, f"h{i - 1}"] = round(diff, 6)
  result += f"\b\b]{' *' if og_hit_steps_sd < 0.001 else ''}\tmean:{og_hit_steps_mean} sd:{og_hit_steps_sd}\n    ["
  for i in range(1, num_mods):
    mod_df = curr[i]
    mod_miss_steps_mean = num_from_df(mod_df, "miss_steps", "value")
    mod_miss_steps_sd = num_from_df(mod_df, "miss_steps", "std_dev")
    diff = (mod_miss_steps_mean - og_miss_steps_mean) / og_miss_steps_sd
    result += f"m{i - 1}:{round(diff, 6)}; "
    averages[2][i - 1] += diff
    df.loc[bod, f"m{i - 1}"] = round(diff, 6)
  result += f"\b\b]{' *' if og_miss_steps_sd < 0.001 else ''}\tmean:{og_miss_steps_mean} sd:{og_miss_steps_sd}\n    ["
  for i in range(1, num_mods):
    mod_df = curr[i]
    mod_capac_mean = num_from_df(mod_df, "capacitance", "value")
    mod_capac_sd = num_from_df(mod_df, "capacitance", "std_dev")
    diff = (mod_capac_mean - og_capac_mean) / og_capac_sd
    result += f"c{i - 1}:{round(diff, 6)}; "
    averages[3][i - 1] += diff
    df.loc[bod, f"c{i - 1}"] = round(diff, 6)
  result += f"\b\b]{' *' if og_capac_sd < 0.001 else ''}\tmean:{og_capac_mean} sd:{og_capac_sd}"
  result += "\n\n"
result += "AVERAGES:\n"
df.loc["AVERAGES"] = [round(e / len(everything.keys()), 6) for lst in averages for e in lst]
for sublist in averages:
  result += f"    ["
  for e in sublist:
    e /= len(everything.keys())
    result += f"{round(e, 6)}; "
  result += f"\b\b]\n"

# Write output into the output files
with open("out.txt", "w") as f:
  f.write(result)
df.to_csv("out.csv")
