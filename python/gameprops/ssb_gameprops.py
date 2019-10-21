from gameprops.gameprops import *
from shared_constants import Constants
from nn_utils import *
import numpy as np

# A subclass of the GameProps specific to Super Smash Brothers for the Nintendo 64 Entertainment System (tm) (c).
# We need to know the number of possible states (which varies depending on character), as well
class SSBGameProps(GameProps):

    def __init__(self):
        # First, calculate the number of inputs based on the number of possible states
        NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
        OUTPUT_LENGTH = 24 # based on number of possible inputs in gameConstants.lua

        self.num_possible_states = NUM_POSSIBLE_STATES
        # taken from number of non-state params in client data, multiplied by 2 players
        input_length = (Constants.NUM_FRAMES_PER_STATE * (self.num_possible_states + 13) * 2)

        self.learning_rate = 1e-4

        # After that, call the superclass' init method as normal
        super(SSBGameProps, self).__init__(Games.SSB, input_length, OUTPUT_LENGTH)

        # Pong should only need one smaller hidden layer
        self.num_hidden_layers = 4
        self.set_hidden_units_array([4000, 4000, 2000, 500])
        self.future_reward_discount = 0.99425 # Rewards 2 seconds into the future are worth 50%

        self.experience_buffer_size = 200000
        self.num_obs_before_training = 1000

        # Slowly make agent less random
        self.num_steps_epislon_decay = 2000000
        self.epsilon_end =  0.1
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay

        # Once we start acting almost-optimally, slow down the rate at which the agent gets less random
        self.finetune_epsilon_end = 0.01
        self.finetune_num_steps_before_epsilon_end = 10000000
        self.finetune_step_size = (self.epsilon_end - self.finetune_epsilon_end) / self.finetune_num_steps_before_epsilon_end

    def get_num_possible_states(self):
        return self.num_possible_states

    # This method converts all of the ssb data to a format that can be fed as inputs into the network
    def convert_state_to_network_input(self, state):
        # Iterate through each state's frames, and then through each player's data
        tf_data = []
        for i in range(state.get_num_frames()):
            # Normalize the data to (try and) get the data from 0-1.
            data = state.get_frame(i)

            # Append numeric data to vector. DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
            for player_id in range(1, 3):
                tf_data.append(self.normalize(data.get(str(player_id)+"xp"), 0.00025, str(player_id)+"xp"))
                tf_data.append(self.normalize(data.get(str(player_id)+"xv"), 0.01, str(player_id)+"xv"))
                tf_data.append(self.normalize(data.get(str(player_id)+"xa"), 0.01, str(player_id)+"xa"))
                tf_data.append(self.normalize(data.get(str(player_id)+"yp"), 0.0003, str(player_id)+"yp"))
                tf_data.append(self.normalize(data.get(str(player_id)+"yv"), 0.01, str(player_id)+"yv"))
                tf_data.append(self.normalize(data.get(str(player_id)+"ya"), 0.1, str(player_id)+"ya"))
                tf_data.append(self.normalize(data.get(str(player_id)+"shld"), 0.018, str(player_id)+"shld"))
                tf_data.append(self.normalize(data.get(str(player_id)+"shld_rec"), 0.1, str(player_id)+"shld_rec"))
                tf_data.append(self.normalize(data.get(str(player_id)+"jumps"), 0.5, str(player_id)+"jumps"))
                tf_data.append(self.normalize(data.get(str(player_id)+"dmg"), 0.01, str(player_id)+"dmg"))
                tf_data.append(data.get(str(player_id)+"is_air"))
                tf_data.append(self.normalize(data.get(str(player_id)+"state_frame"), 0.02, str(player_id)+"state_frame"))

                # dir is -1 to 1. Make it 0 to 1
                dir_val = data.get(str(player_id)+"dir")
                if dir_val == -1:
                    tf_data.append(0)
                else:
                    tf_data.append(1)

                # Convert the categorical state variable into binary data
                tf_data = tf_data + self.convert_state_to_vector(data.get(str(player_id)+"state"), self.num_possible_states)
        return tf_data

    def normalize(self, datum_val, scale, keyfordebugging):
        return datum_val * scale

    # This method converts the state of the player into a one-hot vector. Required since
    # the state doesn't really mean anything in a numerical sense.
    def convert_state_to_vector(self, state_value, num_possible_states):
        v = [0] * num_possible_states
        try:
            v[state_value] = 1
        except:
            print(state_value)
            print(v)
            raise Exception("State value exceeded expected maximum number of states!")

        return v