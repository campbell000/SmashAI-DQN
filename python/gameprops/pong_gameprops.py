from gameprops.gameprops import *
from shared_constants import Constants
from shared_constants import SharedConstants
from gamedata_parser import *
import numpy as np

# A subclass of the GameProps specific to Pong.
class PongGameProps(GameProps):

    # Pong currently has  6 inputs (see convert_state_to_network()) and 5 outputs (slow/fast up, slow/fast down, nothing)
    def __init__(self):
        shared_props = SharedConstants()
        self.pong_input_length = shared_props.get_prop_val('pong', 'num_frames_per_state') * 4
        super(PongGameProps, self).__init__(self.pong_input_length, 3) # 3 actions: up, down, and stand still
    # format the data like this: [p1score, p1pos, p2score, p2pos, ballx, bally] for each frame in the state
    def convert_state_to_network_input(self, state, reverse=False):
        input = np.zeros((self.pong_input_length))
        for i in range(state.get_num_frames()):
            data = PongGameData(state.get_frame(i))
            base_index = i * 4
            input[base_index+0] = data.get_paddle_y_pos(1)
            input[base_index+1] = data.get_paddle_y_pos(2)
            input[base_index+2] = data.get_ball_x_pos()
            input[base_index+3] = data.get_ball_y_pos()
        return input