import os

# This class is responsible for printing metrics to a file as the bot is being trained.
class Evaluator:
    def __init__(self, rewarder, buffer_size=50000 ):
        self.buffer = buffer_size
        self.max_q_values = {}
        self.avg_rewards = []
        self.losses = []
        self.current_kills=0
        self.rewarder = rewarder
        try:
            os.remove("average_q_values.txt")
        except:
            a = 1

        try:
            os.remove("KOs_per_episode.txt")
        except:
            a = 1

        try:
                os.remove("loss.txt")
        except:
            a = 1

        try:
            os.remove("avg_reward.txt")
        except:
            a = 1
        self.iteration = 0

    def add_q_value(self, maxQ):
        self.max_q_values[self.iteration] = maxQ
        self.iteration += 1
        if len(self.max_q_values) >= self.buffer:
            self.dump_buffer()

    def add_avg_reward(self, reward):
        self.avg_rewards.append(reward)
        if len(self.avg_rewards) >= self.buffer:
            self.dump_reward_buffer()

    def dump_reward_buffer(self):
        with open('avg_reward.txt', 'a') as file:
            for k in self.avg_rewards:
                file.write(str(k)+"\n")

        self.avg_rewards = []

    def add_loss(self, loss):
        self.losses.append(loss)
        if len(self.losses) >= self.buffer:
            self.dump_loss_buffer()

    def dump_loss_buffer(self):
        with open('loss.txt', 'a') as file:
            for k in self.losses:
                file.write(str(k)+"\n")

        self.losses = []

    def dump_buffer(self):
        with open('average_q_values.txt', 'a') as file:
            for k in self.max_q_values:
                file.write(str(k)+","+str(self.max_q_values[k])+"\n")

        self.max_q_values = {}

    def add_kill_reward_state(self, experience):
        if self.rewarder.bot_killed_opponent(experience):
            self.current_kills += 1

        if self.rewarder.opponent_killed_bot(experience):
            with open('KOs_per_episode.txt', 'a') as file:
                file.write(str(self.current_kills)+"\n")
            self.current_kills = 0
