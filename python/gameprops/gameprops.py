# This abstract class contains all game-specific properties related to training the neural networks. It contains things
# the number of inputs/outputs, the network parameters, the parameters for the DQN process, etc.

from enum import Enum
class Games(Enum):
    PONG = 1
    SSB = 2

class GameProps():

    # Initialize defaults for all of the variables
    def __init__(self, gameType, network_input_len, network_output_len):
        self.gameType = gameType
        self.learning_rate = 1e-4
        self.network_input_length = network_input_len
        self.network_output_length = network_output_len

        self.experience_buffer_size = 10000
        self.future_reward_discount = 0.99
        self.mini_batch_size = 100
        self.num_obs_before_training = 10000
        self.num_steps_epislon_decay = 500000
        self.epsilon_end =  0.05
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay

        # based on https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw
        num_hidden = int(self.network_input_length * .6666)
        self.num_hidden_layers = 2
        self.hidden_units_arr = [ num_hidden, int(num_hidden/2)]

    def convert_state_to_network_input(self, state):
        pass

    # returns a "Games" value indicating the game that this GameProps object is associated with
    def get_game(self):
        return self.gameType

    def get_learning_rate(self):
        return self.learning_rate

    def get_network_input_len(self):
        return self.network_input_length

    def get_network_output_len(self):
        return self.network_output_length

    def get_experience_buffer_size(self):
        return self.experience_buffer_size

    def get_future_reward_discount(self):
        return self.future_reward_discount

    def get_mini_batch_size(self):
        return self.mini_batch_size

    def get_num_obs_before_training(self):
        return self.num_obs_before_training

    def get_num_steps_epsilon_decay(self):
        return self.num_steps_epislon_decay

    def get_epsilon_step_size(self):
        return self.epsilon_step_size

    def get_num_hidden_layers(self):
        return self.num_hidden_layers

    def get_hidden_units_array(self):
        return self.hidden_units_arr

    def get_epsilon_end(self):
        return self.epsilon_end

    def set_game(self, v):
        self.gameType = v

    def set_learning_rate(self, v):
        self.learning_rate = v

    def set_network_input_len(self, v):
        self.network_input_length = v

    def set_network_output_len(self, v):
        self.network_output_length = v

    def set_experience_buffer_size(self, v):
        self.experience_buffer_size = v

    def set_future_reward_discount(self, v):
        self.future_reward_discount = v

    def set_mini_batch_size(self, v):
        self.mini_batch_size = v

    def set_num_obs_before_training(self, v):
        self.num_obs_before_training = v

    def set_num_steps_epsilon_decay(self, v):
        self.num_steps_epislon_decay = v

    def set_epsilon_step_size(self, v):
        self.epsilon_step_size = v

    def set_num_hidden_layers(self, v):
        self.num_hidden_layers = v

    def set_hidden_units_array(self, v):
        self.hidden_units_arr = v

