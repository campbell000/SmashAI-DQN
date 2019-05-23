from gameprops.gameprops import *
from shared_constants import Constants
from nn_utils import *

# A subclass of the GameProps specific to Super Smash Brothers for the Nintendo 64 Entertainment System (tm) (c).
# We need to know the number of possible states (which varies depending on character), as well
class SSBGameProps(GameProps):

    def __init__(self, gameType, network_output_len, num_possible_states):
        # First, calculate the number of inputs based on the number of possible states
        self.num_possible_states = num_possible_states
        input_length = (Constants.NUM_FRAMES_PER_STATE * (self.num_possible_states + 13) * 2) # taken from number of non-state params in client data, multiplied by 2 players

        # After that, call the superclass' init method as normal
        super(SSBGameProps, self).__init__(gameType, input_length, network_output_len)

    def get_num_possible_states(self):
        return self.num_possible_states

    # This method converts all of the ssb data to a format that can be fed as inputs into the network
    def convert_state_to_network_input(self, state):
        # Iterate through each state's frames, and then through each player's data
        tf_data = []
        for frame in sorted(state.get_frames()):
            for player_data in sorted(frame.get_players()):
                # Append numeric data to vector. DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
                tf_data.append(player_data["xp"])
                tf_data.append(player_data["xv"])
                tf_data.append(player_data["xa"])
                tf_data.append(player_data["yp"])
                tf_data.append(player_data["yv"])
                tf_data.append(player_data["ya"])
                tf_data.append(player_data["shield_size"])
                tf_data.append(player_data["shield_recovery_time"])
                tf_data.append(player_data["direction"])
                tf_data.append(player_data["jumps_remaining"])
                tf_data.append(player_data["damage"])
                tf_data.append(player_data["state_frame"])
                tf_data.append(player_data["is_in_air"])

                # Convert the categorical state variable into binary data
                tf_data = tf_data + self.convert_state_to_vector(player_data["state"], self.num_possible_states)
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