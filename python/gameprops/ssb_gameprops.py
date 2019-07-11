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
        OUTPUT_LENGTH = 54 # based on number of possible inputs in gameConstants.lua
        self.num_possible_states = NUM_POSSIBLE_STATES
        # taken from number of non-state params in client data, multiplied by 2 players
        input_length = (Constants.NUM_FRAMES_PER_STATE * (self.num_possible_states + 14) * 2)

        # After that, call the superclass' init method as normal
        super(SSBGameProps, self).__init__(Games.SSB, input_length, OUTPUT_LENGTH)

        # Pong should only need one smaller hidden layer
        self.num_hidden_layers = 4
        self.set_hidden_units_array([10000, 5000, 5000, 5000])
        self.future_reward_discount = 1 - 1e-3

    def get_num_possible_states(self):
        return self.num_possible_states

    # This method converts all of the ssb data to a format that can be fed as inputs into the network
    def convert_state_to_network_input(self, state):
        # Iterate through each state's frames, and then through each player's data
        tf_data = []
        for i in range(state.get_num_frames()):
            data = state.get_frame(i)
            # Append numeric data to vector. DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
            for player_id in range(1, 3):
                tf_data.append(data.get(str(player_id)+"xp"))
                tf_data.append(data.get(str(player_id)+"xv"))
                tf_data.append(data.get(str(player_id)+"xa"))
                tf_data.append(data.get(str(player_id)+"yp"))
                tf_data.append(data.get(str(player_id)+"yv"))
                tf_data.append(data.get(str(player_id)+"ya"))
                tf_data.append(data.get(str(player_id)+"shld"))
                tf_data.append(data.get(str(player_id)+"shld_rec"))
                tf_data.append(data.get(str(player_id)+"dir"))
                tf_data.append(data.get(str(player_id)+"jumps"))
                tf_data.append(data.get(str(player_id)+"dmg"))
                tf_data.append(data.get(str(player_id)+"state"))
                tf_data.append(data.get(str(player_id)+"is_air"))
                tf_data.append(data.get(str(player_id)+"state_frame"))

                # Convert the categorical state variable into binary data
                tf_data = tf_data + self.convert_state_to_vector(data.get(str(player_id)+"state"), self.num_possible_states)
        return tf_data

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