import numpy as np
import matplotlib.pyplot as plt

ratios ={"pizza": {"pizza": 1, "wasabi": 0.48, "snowball": 1.52, "shells": 0.71},
         "wasabi": {"pizza": 2.05, "wasabi": 1, "snowball": 3.26, "shells": 1.56},
         "snowball": {"pizza": 0.64, "wasabi": 0.3, "snowball": 1, "shells": 0.46},
         "shells": {"pizza": 1.41, "wasabi": 0.61, "snowball": 2.08, "shells": 1}}

avil_capital = 1
traders = {}
for key, val in ratios["shells"].items():
    for key2, val2 in ratios[key].items():
        for key3, val3 in ratios[key2].items():
            for key4, val4 in ratios[key3].items():
                traders[f"{key} -> {key2} -> {key3} -> {key4} -> shells"] = avil_capital * val * val2 * val3 * val4 * ratios[key4]["shells"]

# print(traders)
# plt.plot(traders.values())
# plt.show()

# print(max(traders.values()))

ind = list(traders.values()).index(max(traders.values()))
keys = list(traders.keys())
print(keys[ind])

# key = list(traders.keys())[28]
# print(f"{key} : {traders[key]}")