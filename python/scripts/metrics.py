import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime

import csv

FILES = [
    "mario_tennis_rewards_dueling-before.txt",
    "mariotennis-nodueling.txt"
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

datecontainer = []
for a in range(len(data)):
    d = data[a]
    datecontainer.append([])
    roottime = datetime.strptime(d[0][0], "%Y-%m-%d %H:%M:%S.%f")
    for i in range(len(d)):
        t = datetime.strptime(d[i][0], "%Y-%m-%d %H:%M:%S.%f")
        diff = (t - roottime).total_seconds()
        datecontainer[a].append(diff)


for i in range(len(xdatacontainer)):
    xdata = xdatacontainer[i]
    ydata = ydatacontainer[i]
    plt.plot(xdata, ydata, label=FILES[i])

plt.legend()
plt.savefig("iterations-vs-reward")
plt.clf()
plt.cla()
plt.close()

for i in range(len(xdatacontainer)):
        xdata = datecontainer[i][:200]
        ydata = ydatacontainer[i][:200]
        plt.plot(xdata, ydata, label=FILES[i])

plt.legend()
plt.savefig("time-vs-reward")
plt.clf()
plt.cla()
plt.close()

for i in range(len(xdatacontainer)):
    xdata = datecontainer[i][:200]
    ydata = xdatacontainer[i][:200]
    plt.plot(xdata, ydata, label=FILES[i])

plt.legend()
plt.savefig("time-vs-iterations")



