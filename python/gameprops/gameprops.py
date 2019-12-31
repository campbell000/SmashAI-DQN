# This abstract class contains all game-specific properties related to training the neural networks. It contains things
# the number of inputs/outputs, the network parameters, the parameters for the DQN process, etc.

from enum import Enum
class Games(Enum):
    PONG = 1
    SSB = 2

class GameProps():

    """
            self.learning_rate = 1e-5
            self.network_input_length = network_input_len
            self.network_output_length = network_output_len

            self.experience_buffer_size = 100000
            self.future_reward_discount = 0.95
            self.mini_batch_size = 32
            self.num_obs_before_training = 1000

            # Slowly make agent less random
            self.anneal_epsilon = True
            self.num_steps_epislon_decay = 1200000
            self.epsilon_end =  0.05
            self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
            self.hidden_units_arr = [256, 256, 256]
    """

    # Initialize defaults for all of the variables
    def __init__(self, network_input_len, network_output_len):
        self.learning_rate = 1e-5
        self.network_input_length = network_input_len
        self.network_output_length = network_output_len

        self.experience_buffer_size = 100000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 1000

        # Slowly make agent less random
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 1200000
        self.epsilon_end =  0.05
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.hidden_units_arr = [256, 256, 256]

    def convert_state_to_network_input(self, state):
        pass

    def is_conv(self):
        return False

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

