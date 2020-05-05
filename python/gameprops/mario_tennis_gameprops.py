from gameprops.gameprops import *
from shared_constants import Constants
from shared_constants import SharedConstants
from nn_utils import *
import numpy as np
from nn_utils import NeuralNetworkUtils as NNUtils

class MarioTennisGameprops(GameProps):

    def __init__(self):
        shared_props = SharedConstants()
        self.num_frames_per_state = shared_props.get_prop_val('mario_tennis', 'num_frames_per_state')
        self.NUM_BALL_SPIN_STATES = 16 # number of possible ball spin states (topspin, slice, etc)
        self.network_input_length = (self.num_frames_per_state * (16 + self.NUM_BALL_SPIN_STATES))
        self.network_output_length = 19
        super(MarioTennisGameprops, self).__init__(self.network_input_length, self.network_output_length)

        self.learning_rate = 1e-5
        self.experience_buffer_size = 500000
        self.future_reward_discount = 0.99
        self.mini_batch_size = 32
        self.num_obs_before_training = 10000
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 1000000
        self.epsilon_end =  0.1
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.hidden_units_arr = [1024, 1024, 1024, 1024, 512]

        # Second schedule so that it goes from 1 to 0.1 in 4,000,000, and then from 0.1 to 0.01 in 1,000,000
        self.second_num_steps_epislon_decay = 1000000
        self.second_epsilon_end = 0.01
        self.second_epsilon_step_size = (self.epsilon_end - self.second_epsilon_end) / self.second_num_steps_epislon_decay

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
        self.ball_spin_enums[16] = 15

    def get_num_possible_states(self):
        return self.num_possible_states

    def convert_state_to_network_input(self, state, reverse=False):
        X_POS_MAX = 120
        Y_POS_MAX = 26
        Z_POS_MAX = 266
        X_POS_MIN = -120
        Y_POS_MIN = 18.6
        Z_POS_MIN = -266
        CHARGE_MIN = 0
        CHARGE_MAX = 50
        BALL_X_MAX = 120
        BALL_X_MIN = -120
        BALL_Y_MAX = 100
        BALL_Y_MIN = 0
        BALL_Z_MAX = 280
        BALL_Z_MIN = -280
        input = np.zeros((self.network_input_length))
        for i in range(state.get_num_frames()):
            data = state.get_frame(i)
            base_index = int(i * (self.network_input_length / self.num_frames_per_state))
            # Build flat array, but normalize values between -1 and 1
            #TODO: WE ARE SIMPLIFYING RIGHT NOW BY ASSUMING CPU IS ALWAYS CLOSEST TO PLAYER
            input[base_index+0] = NNUtils.normalize(data.get("1x"), X_POS_MIN, X_POS_MAX)
            input[base_index+1] = NNUtils.normalize(data.get("1y"), Y_POS_MIN, Y_POS_MAX)
            input[base_index+2] = NNUtils.normalize(data.get("1z"), Z_POS_MIN, Z_POS_MAX)
            input[base_index+3] = -1 if data.get("1srv") == 0 else 1
            input[base_index+4] = NNUtils.normalize(data.get("1chrg"), CHARGE_MIN, CHARGE_MAX)
            input[base_index+5] = NNUtils.normalize(data.get("2x"), X_POS_MIN, X_POS_MAX)
            input[base_index+6] = NNUtils.normalize(data.get("2y"), Y_POS_MIN, Y_POS_MAX)
            input[base_index+7] = NNUtils.normalize(data.get("2z"), Z_POS_MIN, Z_POS_MAX)
            input[base_index+8] = -1 if data.get("2srv") == 0 else 1
            input[base_index+9] = NNUtils.normalize(data.get("2chrg"), CHARGE_MIN, CHARGE_MAX)
            input[base_index+10] = NNUtils.normalize(data.get("bx"), BALL_X_MIN, BALL_X_MAX)
            input[base_index+11] = NNUtils.normalize(data.get("by"), BALL_Y_MIN, BALL_Y_MAX)
            input[base_index+12] = NNUtils.normalize(data.get("bz"),BALL_Z_MIN, BALL_Z_MAX)
            input[base_index+13] = 1 if data.get("play") == 0 else -1

            # Add 2 additional inputs for is_charging to help it a little bit ;)
            input[base_index+14] = 1 if data.get("1chrg") > 0 else -1
            input[base_index+15] = 1 if data.get("2chrg") > 0 else -1

            # Convert ball spin type to one hot encoding
            spin = np.argmax(self.encode_spin_type(data.get("bspin")))
            if input[base_index+16+spin] != 0:
                raise Exception("Something is wrong with the spin logic")

            input[base_index+16+spin] = 1

        return input

    def encode_spin_type(self, spin_val):
        normalized_ball_spin_val = 0

        # Not sure why, but every 400,000 or so frames, we get some weird value here.
        try:
            normalized_ball_spin_val = self.ball_spin_enums[int(spin_val)]
        except:
            a = 3

        v = -1 * np.zeros(self.NUM_BALL_SPIN_STATES)
        try:
            v[normalized_ball_spin_val] = 1
        except:
            print(spin_val)
            print(v)
            raise Exception("State value exceeded expected maximum number of states!")
        return v
