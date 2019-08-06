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

        self.experience_buffer_size = 100000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 100000

        # Slowly make agent less random
        self.num_steps_epislon_decay = 1000000
        self.epsilon_end =  0.2
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay

        # based on https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw
        num_hidden = int(self.network_input_length * .6666)
        self.num_hidden_layers = 2
        self.hidden_units_arr = [num_hidden, int(num_hidden/2)]

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

    def get_finetuned_epsilon_end(self):
        return self.finetune_epsilon_end

    def get_finetuned_num_steps_before_epsilon_end(self):
        return self.finetune_num_steps_before_epsilon_end

    def get_finetuned_step_size(self):
        return self.finetune_step_size

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
        print("num_hidden_layers: "+str(self.num_hidden_layers))
        print("hidden_units_arr: "+str(self.hidden_units_arr))
        print("Learning Rate: "+str(self.learning_rate))
        print("Fine-tuned epsilon end: "+str(self.finetune_epsilon_end))
        print("Fine-tuned num epsilon steps: "+str(self.finetune_num_steps_before_epsilon_end))
        print("Fine-tuned epsilon step size: "+str(self.finetune_step_size))

