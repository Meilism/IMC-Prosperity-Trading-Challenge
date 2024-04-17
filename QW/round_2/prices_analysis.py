import numpy as np, pandas as pd
import matplotlib.pyplot as plt

filenames = ["codes/round_2/round-2-island-data-bottle/prices_round_2_day_-1.csv",
             "codes/round_2/round-2-island-data-bottle/prices_round_2_day_0.csv",
             "codes/round_2/round-2-island-data-bottle/prices_round_2_day_1.csv",]

sample_data = {}
for i, fname in enumerate(filenames):
    day = f"day_{i-1}"
    sample_data[day] = {} # day -1, 0, 1

    df = pd.read_csv(fname, sep=";")
    sample_data[day]["orchids"] = df["ORCHIDS"].to_numpy()
    sample_data[day]["sunlight"] = df["SUNLIGHT"].to_numpy()
    sample_data[day]["humidity"] = df["HUMIDITY"].to_numpy()

    if i == 0:
        sample_data[day]["timstamp"] = df["timestamp"].to_numpy()
    else:
        sample_data[day]["timstamp"] = df["timestamp"].to_numpy() + sample_data[f"day_{i-2}"]["timstamp"][-1] + 1

fig, ax = plt.subplots(figsize=(15, 5))
fig.subplots_adjust(right=0.85)
ax_twin1 = ax.twinx()
ax_twin2 = ax.twinx()
ax_twin2.spines.right.set_position(("axes", 1.1))
colors = ["red", "green", "blue"]
axes = [ax, ax_twin1, ax_twin2]
p_list = []
for j, item in enumerate(["orchids", "sunlight", "humidity"]):
    for i in [-1, 0, 1]:
        p, = axes[j].plot(sample_data[f"day_{i}"]["timstamp"], sample_data[f"day_{i}"][item], color=colors[j], label=f"{item}")
    
    p_list.append(p)
    axes[j].yaxis.label.set_color(colors[j])
    axes[j].tick_params(axis='y', colors=colors[j])

ax_twin1.axhline(2500, linestyle=':', color=colors[1])
ax_twin2.axhline(60, linestyle=':', color=colors[2])
ax_twin2.axhline(80, linestyle=':', color=colors[2])

ax.set_ylabel("orchids")
ax_twin1.set_ylabel("sunlight")
ax_twin2.set_ylabel("humidity")

ax.legend(handles=p_list, loc="upper right")
plt.show()