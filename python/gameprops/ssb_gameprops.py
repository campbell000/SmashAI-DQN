from gameprops.gameprops import *
from shared_constants import Constants
from shared_constants import SharedConstants
from nn_utils import *
import numpy as np
from nn_utils import NeuralNetworkUtils as NNUtils

# A subclass of the GameProps specific to Super Smash Brothers for the Nintendo 64 Entertainment System (tm) (c).
# We need to know the number of possible states (which varies depending on character), as well
class SSBGameProps(GameProps):

    # "BIG" SET AS OF APRIL 2020
    def __init__(self):
        # First, calculate the number of inputs based on the number of possible states
        NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
        OUTPUT_LENGTH = 24 # based on number of possible inputs in gameConstants.lua

        self.num_possible_states = NUM_POSSIBLE_STATES

        # taken from number of non-state params in client data, multiplied by 2 players
        shared_props = SharedConstants()
        input_length = (shared_props.get_prop_val('smash', 'num_frames_per_state') * (self.num_possible_states + 11) * 2)

        # After that, call the superclass' init method as normal
        super(SSBGameProps, self).__init__(input_length, OUTPUT_LENGTH)

        self.learning_rate = 1e-6

        self.experience_buffer_size = 500000
        self.future_reward_discount = 0.96
        self.mini_batch_size = 32
        self.num_obs_before_training = 10000

        # Slowly make agent less random
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 4000000
        self.epsilon_end =  0.1
        self.second_num_steps_epislon_decay = 1000000
        self.second_epsilon_end = 0.01
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.second_epsilon_step_size = (self.epsilon_end - self.second_epsilon_end) / self.second_num_steps_epislon_decay
        self.hidden_units_arr = [5000, 5000, 5000, 5000, 2000, 1000]

    """
    GOOD SMALL SET as of MARCH 2020
        # First, calculate the number of inputs based on the number of possible states
        NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
        OUTPUT_LENGTH = 24 # based on number of possible inputs in gameConstants.lua

        self.num_possible_states = NUM_POSSIBLE_STATES
        # taken from number of non-state params in client data, multiplied by 2 players
        input_length = (Constants.NUM_FRAMES_PER_STATE * (self.num_possible_states + 11) * 2)

        # After that, call the superclass' init method as normal
        super(SSBGameProps, self).__init__(input_length, OUTPUT_LENGTH)

        self.learning_rate = 1e-5

        self.experience_buffer_size = 100000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 10000

        # Slowly make agent less random
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 2000000
        self.epsilon_end =  0.1
        self.second_num_steps_epislon_decay = 1000000
        self.second_epsilon_end = 0.01
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.second_epsilon_step_size = (self.epsilon_end - self.second_epsilon_end) / self.second_num_steps_epislon_decay
        self.hidden_units_arr = [5000, 5000, 2000, 2000, 1000]
    
    """



    # This method converts all of the ssb data to a format that can be fed as inputs into the network
    def convert_state_to_network_input(self, state, reverse=False):
        # Iterate through each state's frames, and then through each player's data
        tf_data = []
        for i in range(state.get_num_frames()):
            # Normalize the data to (try and) get the data from 0-1.
            data = state.get_frame(i)

            # If reverse = false, make player 1 the first half of the inputs, and player 2 the second half. If true,
            # do the opposite. Useful for self-training.
            player_order = range(1, 3) if not reverse else reversed(range(1, 3))

            # Append numeric data to vector. DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
            for player_id in player_order:
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"xp"), -9000, 9000))
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"xv"), -70, 70))
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"yp"), -9000, 9000))
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"yv"), -9000, 9000))
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"shld"), 0, 55))

                # TODO: change based on character
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"jumps"), 0, 2))

                # Add variable to indicate whether or not the player can jump
                if data.get(str(player_id)+"jumps") == 0:
                    tf_data.append(-1)
                else:
                    tf_data.append(1)

                # IS IN AIR is 0 to 1. Make it -1 to 1
                if data.get(str(player_id)+"is_air") == 0:
                    tf_data.append(-1)
                else:
                    tf_data.append(1)

                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"dmg"), 0, 200))
                tf_data.append(NNUtils.normalize(data.get(str(player_id)+"state_frame"), 0, 100))
                tf_data.append(data.get(str(player_id)+"dir"))
                tf_data = tf_data + self.convert_state_to_vector(data.get(str(player_id)+"state"), self.num_possible_states)

        return tf_data

    # This method converts the state of the player into a one-hot vector. Required since
    # the state doesn't really mean anything in a numerical sense.
    def convert_state_to_vector(self, state_value, num_possible_states):
        v = [-1] * num_possible_states
        try:
            v[state_value] = 1
        except:
            print(state_value)
            print(v)
            print("State value exceeded expected maximum number of states!")

        return v