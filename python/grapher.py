import matplotlib.pyplot as plt
SAMPLE_RATE = 10000
arr = []
i = 0

"""
with open("average_q_values.txt") as f:
  for line in f:
    if i % SAMPLE_RATE == 0:
      num = float(line.split(",")[1])
      arr.append(num)
    i = i + 1
     
plt.plot(arr)
plt.show()
"""
SAMPLE_RATE = 100
arr = []
i = 0
with open("avg_reward.txt") as f:
  for line in f:
    if i % SAMPLE_RATE == 0:
      num = float(line)
      arr.append(num)
    i = i + 1
     
plt.plot(arr)
plt.show()