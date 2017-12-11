import os
class Evaluator:
    def __init__(self, rewarder, buffer_size=50000 ):
        self.buffer = buffer_size
        self.max_q_values = {}
        self.current_kills=0
        self.rewarder = rewarder
        try:
            os.remove("max_q_values.txt")
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
        self.iteration = 0

    def add_q_value(self, maxQ):
        self.max_q_values[self.iteration] = maxQ
        self.iteration += 1
        if len(self.max_q_values) >= self.buffer:
            self.dump_buffer()

    def dump_buffer(self):
        with open('max_q_values.txt', 'a') as file:
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

    def record_loss(self, loss):
        with open('loss.txt', 'a') as file:
            file.write(str(loss)+"\n")

