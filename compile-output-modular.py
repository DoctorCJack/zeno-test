import re
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math

def num_from_df(df, name, type):
  result = list(df.loc[(df["name"] == name) & (df["type"] == type)]["value"])[0] # There should always be exactly one element in this list
  result = float(("%.8f" % float(result)).rstrip('0').rstrip('.')) # Converts a string in scientific notation to a float I can work with
  return result

# Get the number of expansions from config.cfg
with open("config.cfg", "r") as f:
  s = f.read()
  num_expansions = int(re.search("numExpansions=([0-9]+)", s).groups()[0])
  num_iters = int(re.search("numIters=([0-9]+)", s).groups()[0])

# Instantiate stuff
everything = dict(list()) # Dictionary where keys are bods and values are 2D lists of dataframes
dir = "./csvs-modular" # Where the input csvs are located
num_mods = 2 + num_expansions # The first 2 are zeno-original and the base case in zeno-modified
averages = [[0] * (num_mods - 1) for i in range(4)]
interior_abs = False # Determines if we get the absolute value of the capacitance difference before or after averaging them

# Process the files and put all the necessary data into data structures
for filename in os.listdir(dir):
  csv = pd.read_csv(os.path.join(dir, filename))
  csv.columns = ["name", "type", "value"]
  # Matches on the filename to get the list [<iteration number>, <bod filename>, <expansion option>]
  regex = re.search("^([0-9]+)-(.*)-([0-9]+).csv$", filename)
  # If the filename didn't match, then match on the filename to get the list [<iteration number>, <bod filename>, "control"]
  if(regex == None):
    regex = re.search("^([0-9+])-(.*)-(control).csv$", filename)
  g = regex.groups()
  # g[0] is the iteration number
  # g[1] is the bod filename
  # g[2] is the expansion option
  if g[1] not in everything.keys():
    everything[g[1]] = [list(range(num_mods)) for _ in range(num_iters)] # 2D list where the first index is the iteration and the second index is the expansion option
  if g[2] != "control":
    everything[g[1]][int(g[0])][int(g[2]) + 1] = csv
  else:
    everything[g[1]][int(g[0])][0] = csv

# Do the same thing as for the non-modular version, but for each iteration separately
for iter in range(num_iters):
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
    curr = everything[bod][iter]
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
      diff = abs(diff) if interior_abs else diff
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
  if not os.path.isdir("./outs"):
    os.mkdir("./outs")
  with open(f"outs/out-{iter}.txt", "w") as f:
    f.write(result)
  df.to_csv(f"outs/out-{iter}.csv")

# Compile the output files in ./outs
final_dfs = list(range(num_iters)) # List of dataframes
for i in range(num_iters):
  final_dfs[i] = pd.read_csv(f"outs/out-{i}.csv").iloc[-1:, 1:] # So that I only have the numbers on the row AVERAGES

result = None
for df in final_dfs:
  if type(result) == type(None):
    result = df
  else:
    result += df

result /= num_iters

result.to_csv("out-modular.csv")
# This redundancy is done so that I can make sure the csv is saved properly during debugging. The redundancy may be removed later.
data = pd.read_csv("out-modular.csv")

# Graph the total step differences and the absolute capacitance differences
nums = list(range(num_mods - 1))
steps = data.iloc[:,1:num_mods].values.tolist()[0]
capac = [abs(i) for i in data.iloc[:,(-num_mods + 1):].values.tolist()[0]]
colors = ['red'] * 1 + ['orange'] * 5 + ['yellow'] * 3 + ['green'] * 9 + ['blue'] * 1

cap = 2.0 * (2.0 / math.sqrt(math.pi)) if interior_abs else 1.0

red_patch = mpatches.Patch(color='red', label='Control')
orange_patch = mpatches.Patch(color='orange', label='Constant >=e')
yellow_patch = mpatches.Patch(color='yellow', label='Constant <e')
green_patch = mpatches.Patch(color='green', label='Proportional')
blue_patch = mpatches.Patch(color='blue', label='Random')

plt.bar(nums, steps, align='center', alpha=0.5, color=colors)
plt.xticks(nums, nums)
plt.xlabel('Method of Expansion Number')
plt.ylabel('Difference in standard deviations')
plt.errorbar(nums, steps, yerr = 1, fmt ='_', color = 'black')
plt.title('Total Steps')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.savefig("steps_large_modular.png")

plt.clf()
plt.bar(nums, capac, align='center', alpha=0.5, color=colors)
plt.xticks(nums, nums)
plt.xlabel('Method of Expansion Number')
if interior_abs:
  plt.ylabel('|Absolute difference in standard deviations|')
else:
  plt.ylabel('|Difference in standard deviations|')
plt.errorbar(nums, capac, yerr = 1, fmt ='_', color = 'black')
plt.title('Capacitance')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.axhline(y = cap, color='r', linestyle='-')
plt.savefig("capac_large_modular.png")

# Create a boolean list that represents the indices of expansion options with a capacitance difference less than cap
remainders = [True if i < cap else False for i in capac]
remainder_steps = [i for i, r in zip(steps, remainders) if r]
remainder_capac = [i for i, r in zip(capac, remainders) if r]
remainder_colors = [i for i, r in zip(colors, remainders) if r]
remainder_nums = [i for i, r in zip(nums, remainders) if r]
remainder_range = list(range(len(remainder_nums)))

# Graph the same graphs as before, but only include the expansion options for which the capacitance is less than cap
plt.clf()
plt.bar(remainder_range, remainder_steps, align='center', alpha=0.5, color=remainder_colors)
plt.xticks(remainder_range, remainder_nums)
plt.xlabel('Method of Expansion Number')
plt.ylabel('Difference in standard deviations')
plt.title('Total Steps')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.savefig("steps_small_modular.png")

plt.clf()
plt.bar(remainder_range, remainder_capac, align='center', alpha=0.5, color=remainder_colors)
plt.xticks(remainder_range, remainder_nums)
plt.xlabel('Method of Expansion Number')
if interior_abs:
  plt.ylabel('|Absolute difference in standard deviations|')
else:
  plt.ylabel('|Difference in standard deviations|')
plt.title('Capacitance')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
if interior_abs:
  plt.axhline(y = 2 / math.sqrt(math.pi), color='b', linestyle='-')
plt.savefig("capac_small_modular.png")