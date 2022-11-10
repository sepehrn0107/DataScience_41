from durations_nlp import Duration
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("reviews_extra.csv")
print(df)

ob = {}

for index, row in df.iterrows():
    try:
        text = row["duration"]

        if "old" in text:
            continue

        duration = Duration(text)
        days = duration.to_days()

        if days <= 2 or days > 200:
            continue

        if days > 150:
            print(text)
            print()

        if days not in ob:
            ob[int(days)] = 0
        ob[int(days)] += 1
    except:
        pass

labels = list(ob.keys())
values = list(ob.values())

plt.bar(labels, values, align="center", alpha=0.5)

plt.show()
