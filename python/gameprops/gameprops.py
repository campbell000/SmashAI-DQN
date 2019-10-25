# This abstract class contains all game-specific properties related to training the neural networks. It contains things
# the number of inputs/outputs, the network parameters, the parameters for the DQN process, etc.

from enum import Enum
class Games(Enum):
    PONG = 1
    SSB = 2

class GameProps():

    # Initialize defaults for all of the variables
    def __init__(self, network_input_len, network_output_len):
        self.learning_rate = 1e-4
        self.network_input_length = network_input_len
        self.network_output_length = network_output_len

        self.experience_buffer_size = 100000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 100000

        # Slowly make agent less random
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 400000
        self.epsilon_end =  0.01
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay

        # based on https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw
        num_hidden = int(self.network_input_length * .6666)
        self.hidden_units_arr = [num_hidden, int(num_hidden/2)]

    def convert_state_to_network_input(self, state):
        pass

    def dump(self):
        print("GAMEPROPS")
        print("Learning rate: "+str(self.learning_rate))
        print("network_input_length: "+str(self.network_input_length))
        print("network_output_length: "+str(self.network_output_length))
        print("experience_buffer_size: "+str(self.experience_buffer_size))
        print("future_reward_discount: "+str(self.future_reward_discount))
        print("mini_batch_size: "+str(self.mini_batch_size))
        print("num_obs_before_training: "+str(self.num_obs_before_training))
        print("num_steps_epislon_decay: "+str(self.num_steps_epislon_decay))
        print("epsilon_end: "+str(self.epsilon_end))
        print("epsilon_step_size: "+str(self.epsilon_step_size))
        print("hidden_units_arr: "+str(self.hidden_units_arr))
        print("Learning Rate: "+str(self.learning_rate))

