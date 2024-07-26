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
  dir = os.path.expanduser(re.search("csvs=(.+)", s).groups()[0]) # Where the input csvs are located
  outs = os.path.expanduser(re.search("outs=(.+)", s).groups()[0])

# Instantiate stuff
everything = dict(list()) # Dictionary where keys are bods and values are 2D lists of dataframes
num_mods = 2 + num_expansions # The first 2 are zeno-original and the base case in zeno-modified
interior_abs = False # Determines if we get the absolute value of the capacitance difference before or after averaging them

# Process the files and put all the necessary data into data structures
for filename in os.listdir(dir):
  csv = pd.read_csv(os.path.join(dir, filename))
  csv.columns = ["name", "type", "value"]
  # Matches on the filename to get the list [<iteration number>, <bod filename>, <expansion option>]
  regex = re.search("^([0-9]+)-(.*)-([0-9]+).csv$", filename)
  # If the filename didn't match, then match on the filename to get the list [<iteration number>, <bod filename>, "control"]
  if(regex == None):
    regex = re.search("^([0-9]+)-(.*)-(control).csv$", filename)
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
cols = [f"{c}{i}" for c in ['t', 'h', 'm', 'c'] for i in range(num_mods - 1)]
for iter in range(num_iters):
  # Process the data structures created in the previous step and
  # convert them into the contents of the output files
  df = pd.DataFrame(columns = cols)
  for bod in sorted(everything.keys()):
    averages = [[0] * (num_mods - 1) for _ in range(4)]
    df.loc[bod] = [0.0] * ((num_mods - 1) * 4)
    curr = everything[bod][iter]
    og_df = curr[0]
    og_total_steps_mean = num_from_df(og_df, "total_steps", "value")
    og_hit_steps_mean = num_from_df(og_df, "hit_steps", "value")
    og_miss_steps_mean = num_from_df(og_df, "miss_steps", "value")
    og_capac_mean = num_from_df(og_df, "capacitance", "value")
    for i in range(1, num_mods):
      mod_df = curr[i]
      mod_total_steps_mean = num_from_df(mod_df, "total_steps", "value")
      diff = (mod_total_steps_mean - og_total_steps_mean)
      averages[0][i - 1] += diff
      df.loc[bod, f"t{i - 1}"] = round(diff, 6)
    for i in range(1, num_mods):
      mod_df = curr[i]
      mod_hit_steps_mean = num_from_df(mod_df, "hit_steps", "value")
      diff = (mod_hit_steps_mean - og_hit_steps_mean)
      averages[1][i - 1] += diff
      df.loc[bod, f"h{i - 1}"] = round(diff, 6)
    for i in range(1, num_mods):
      mod_df = curr[i]
      mod_miss_steps_mean = num_from_df(mod_df, "miss_steps", "value")
      diff = (mod_miss_steps_mean - og_miss_steps_mean)
      averages[2][i - 1] += diff
      df.loc[bod, f"m{i - 1}"] = round(diff, 6)
    for i in range(1, num_mods):
      mod_df = curr[i]
      mod_capac_mean = num_from_df(mod_df, "capacitance", "value")
      diff = (mod_capac_mean - og_capac_mean)
      diff = abs(diff) if interior_abs else diff
      averages[3][i - 1] += diff
      df.loc[bod, f"c{i - 1}"] = round(diff, 6)
  df.loc["AVERAGES"] = [round(e / len(everything.keys()), 6) for lst in averages for e in lst]
  for sublist in averages:
    for e in sublist:
      e /= len(everything.keys())

  # Write output into the output files
  if not os.path.isdir(outs):
    print(f"Dir {outs} not found. Creating.")
    os.mkdir(outs)
  df.to_csv(f"{outs}/out-{iter}.csv")

# Compile the output files in ./outs
final_dfs = list(range(num_iters)) # List of dataframes
for i in range(num_iters):
  final_dfs[i] = pd.read_csv(f"{outs}/out-{i}.csv").iloc[-1:, 1:] # So that I only have the numbers on the row AVERAGES

result = pd.DataFrame(0.0, index = ["mean", "std_dev"], columns = cols)
n = 1
for df in final_dfs:
  if n > 1:
    result.loc["std_dev"] += ((((df.iloc[0] - result.loc["mean"]) ** 2) / n) - (result.loc["std_dev"] / (n - 1)))
  result.loc["mean"] += ((df.iloc[0] - result.loc["mean"]) / n)
  n += 1

result.loc["std_dev"] = result.loc["std_dev"] ** 0.5

result.to_csv("out.csv")
data = result # Leftover stuff, may fix in a later update

# Graph the total step differences and the absolute capacitance differences
nums = list(range(num_mods - 1))
steps = data.iloc[0,0:(num_mods - 1)].values.tolist()
steps_sd = data.iloc[1,0:(num_mods - 1)].values.tolist()
capac = [abs(i) for i in data.iloc[0,(-num_mods + 1):].values.tolist()]
capac_sd = [abs(i) for i in data.iloc[1,(-num_mods + 1):].values.tolist()]
colors = ['red'] * 1 + ['orange'] * 5 + ['yellow'] * 3 + ['green'] * 9 + ['blue'] * 1

red_patch = mpatches.Patch(color='red', label='Control')
orange_patch = mpatches.Patch(color='orange', label='Constant >=e')
yellow_patch = mpatches.Patch(color='yellow', label='Constant <e')
green_patch = mpatches.Patch(color='green', label='Proportional')
blue_patch = mpatches.Patch(color='blue', label='Random')

plt.figure(figsize=(9,6))
plt.bar(nums, steps, align='center', alpha=0.5, color=colors)
plt.xticks(nums, nums)
plt.xlabel('Method of Expansion Number')
plt.ylabel('Difference')
plt.errorbar(nums, steps, yerr = steps_sd, fmt ='_', color = 'black')
plt.title('Total Steps')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.savefig("steps_large.png")

plt.clf()
plt.figure(figsize=(9,6))
plt.bar(nums, capac, align='center', alpha=0.5, color=colors)
plt.xticks(nums, nums)
plt.xlabel('Method of Expansion Number')
if interior_abs:
  plt.ylabel('|Absolute difference|')
else:
  plt.ylabel('|Difference|')
plt.errorbar(nums, capac, yerr = capac_sd, fmt ='_', color = 'black')
plt.title('Capacitance')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.axhline(y = capac[0] + capac_sd[0], color='r', linestyle=':')
plt.savefig("capac_large.png")

# Create a boolean list that represents the indices of expansion options we want to keep
c_m = capac[0] # control mean
c_s = capac_sd[0] # control sd
remainders = [True if (c_m + c_s > m - s) else False for (m, s) in zip(capac, capac_sd)]
remainder_steps = [i for i, r in zip(steps, remainders) if r]
remainder_steps_sd = [i for i, r in zip(steps_sd, remainders) if r]
remainder_capac = [i for i, r in zip(capac, remainders) if r]
remainder_capac_sd = [i for i, r in zip(capac_sd, remainders) if r]
remainder_colors = [i for i, r in zip(colors, remainders) if r]
remainder_nums = [i for i, r in zip(nums, remainders) if r]
remainder_range = list(range(len(remainder_nums)))

# Graph the same graphs as before, but only include the expansion options that we want to keep
plt.clf()
plt.figure(figsize=(9,6))
plt.bar(remainder_range, remainder_steps, align='center', alpha=0.5, color=remainder_colors)
plt.xticks(remainder_range, remainder_nums)
plt.xlabel('Method of Expansion Number')
plt.ylabel('Difference')
plt.title('Total Steps')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.savefig("steps_small.png")

plt.clf()
plt.figure(figsize=(9,6))
plt.bar(remainder_range, remainder_capac, align='center', alpha=0.5, color=remainder_colors)
plt.xticks(remainder_range, remainder_nums)
plt.xlabel('Method of Expansion Number')
if interior_abs:
  plt.ylabel('|Absolute difference|')
else:
  plt.ylabel('|Difference|')
plt.title('Capacitance')
plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch])
plt.axhline(y = capac[0] + capac_sd[0], color='r', linestyle=':')
plt.savefig("capac_small.png")