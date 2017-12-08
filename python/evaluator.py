import os
class Evaluator:
    def __init__(self, buffer_size=50000):
        self.buffer = buffer_size
        self.max_q_values = {}
        try:
            os.remove("max_q_values.txt")
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
