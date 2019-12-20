from gameprops.gameprops import *
from shared_constants import Constants
from nn_utils import *
import numpy as np

class MarioTennisGameprops(GameProps):

    def __init__(self):
        self.NUM_BALL_SPIN_STATES = 15 # number of possible ball spin states (topspin, slice, etc)
        self.network_input_length = (Constants.NUM_FRAMES_PER_STATE * (14 + self.NUM_BALL_SPIN_STATES))
        self.network_output_length = 19
        super(MarioTennisGameprops, self).__init__(self.network_input_length, self.network_output_length)

        self.learning_rate = 1e-5
        self.experience_buffer_size = 1000000
        self.future_reward_discount = 0.99
        self.mini_batch_size = 32
        self.num_obs_before_training = 100000
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 8000000
        self.epsilon_end =  0.05
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.hidden_units_arr = [5012, 2048, 2048, 1024]

        self.ball_spin_enums = {}
        self.ball_spin_enums[0] = 0
        self.ball_spin_enums[5] = 1
        self.ball_spin_enums[6] = 2
        self.ball_spin_enums[9] = 3
        self.ball_spin_enums[8] = 4
        self.ball_spin_enums[2] = 5
        self.ball_spin_enums[10] = 6
        self.ball_spin_enums[11] = 7
        self.ball_spin_enums[12] = 8
        self.ball_spin_enums[17] = 9
        self.ball_spin_enums[3] = 10
        self.ball_spin_enums[13] = 11
        self.ball_spin_enums[1] = 12
        self.ball_spin_enums[14] = 13
        self.ball_spin_enums[15] = 14

    def get_num_possible_states(self):
        return self.num_possible_states

    def convert_state_to_network_input(self, state):
        input = np.zeros((self.network_input_length))
        for i in range(state.get_num_frames()):
            data = state.get_frame(i)
            base_index = int(i * (self.network_input_length / Constants.NUM_FRAMES_PER_STATE))
            # Build flat array, but normalize values between -1 and 1
            input[base_index+0] = data.get("1x") / 120
            input[base_index+1] = data.get("1y") / 26
            input[base_index+2] = data.get("1z") / 266
            input[base_index+3] = -1 if data.get("1srv") == 0 else 1
            input[base_index+4] = data.get("1chrg") / 100
            input[base_index+5] = data.get("2x") / 120
            input[base_index+6] = data.get("2y") / 26
            input[base_index+7] = data.get("2z") / 266
            input[base_index+8] = -1 if data.get("2srv") == 0 else 1
            input[base_index+9] = data.get("2chrg") / 100
            input[base_index+10] = data.get("bx") / 120
            input[base_index+11] = data.get("by") / 100
            input[base_index+12] = data.get("bz") / 280
            input[base_index+13] = 1 if data.get("play") == 0 else -1

            # Convert ball spin type to one hot encoding
            spin = np.argmax(self.encode_spin_type(data.get("bspin")))
            if input[base_index+14+spin] != 0:
                raise Exception("Something is wrong with the spin logic")

            input[base_index+14+spin] = 1
        return input

    def encode_spin_type(self, spin_val):
        normalized_ball_spin_val = 0

        # Not sure why, but every 400,000 or so frames, we get some weird value here.
        try:
            normalized_ball_spin_val = self.ball_spin_enums[int(spin_val)]
        except:
            print("We got an unexpected ball curve value: "+str(spin_val))

        v = np.zeros(self.NUM_BALL_SPIN_STATES)
        try:
            v[normalized_ball_spin_val] = 1
        except:
            print(spin_val)
            print(v)
            raise Exception("State value exceeded expected maximum number of states!")
        return v
