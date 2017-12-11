import matplotlib.pyplot as plt

KOS = "KOs_per_episode.txt"
LOSS = "loss.txt"
Q = "max_q_values.txt"

# Plot KO's per episode
#with open(KOS) as f:
#    content = f.readlines()
#content = [x.strip() for x in content]
#plt.plot(content)
#plt.ylabel('KOs Per Episode')
#plt.xlabel('Episode Number')
#plt.ylim([0,2])
#plt.show()

with open(Q) as f:
    content = f.readlines()

final_content = []
for i in range(0, len(content), 1000):
    final_content.append(float(content[i].split(",")[1].strip()))

plt.plot(final_content)
plt.ylabel('Max Q-Value')
plt.ylim([0,3.5])
plt.xlabel('Iterations (divided by 1000 for line smoothness)')
plt.show()