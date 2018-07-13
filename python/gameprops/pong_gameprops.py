from gameprops.gameprops import *
from shared_constants import Constants
from gamedata_parser import *
import numpy as np

# A subclass of the GameProps specific to Super Smash Brothers for the Nintendo 64 Entertainment System (tm) (c).
# We need to know the number of possible states (which varies depending on character), as well
class PongGameProps(GameProps):

    def __init__(self, gameType, network_input_len, network_output_len):
        super(PongGameProps, self).__init__(gameType, network_input_len, network_output_len)

    # format the data like this: [p1score, p1pos, p2score, p2pos, ballx, bally] for each frame in the state
    def convert_state_to_network_input(self, state):
        length = state.get_num_frames() * 6
        input = np.zeros((length))
        for i in range(state.get_num_frames()):
            data = PongGameData(state.get_frame(i))
            base_index = i * 6
            input[base_index+0] = data.get_score(1)
            input[base_index+1] = data.get_paddle_y_pos(1)
            input[base_index+2] = data.get_score(2)
            input[base_index+3] = data.get_paddle_y_pos(2)
            input[base_index+4] = data.get_ball_x_pos()
            input[base_index+5] = data.get_ball_y_pos()
        return input