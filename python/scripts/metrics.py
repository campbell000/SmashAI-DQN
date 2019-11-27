import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

import csv

FILES = [
    "pong_sync_reward_logs.txt",
    "reward_logs.txt"
]

data = []
count = -1
for file in FILES:
    count = count + 1
    data.append([])
    with open(file) as csvfile:
        reader = csv.reader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            data[count].append(row)

xdatacontainer = []
for a in range(len(data)):
    d = data[a]
    xdatacontainer.append([])
    for i in range(len(d)):
        xdatacontainer[a].append(int(d[i][1]))

ydatacontainer = []
for a in range(len(data)):
    d = data[a]
    ydatacontainer.append([])
    for i in range(len(d)):
        ydatacontainer[a].append(float(d[i][2]))

for i in range(len(xdatacontainer)):
    xdata = xdatacontainer[i]
    ydata = ydatacontainer[i]
    plt.plot(xdata, ydata, label=FILES[i])

plt.legend()
plt.savefig("test")