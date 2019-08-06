from gameprops.gameprops import *
from shared_constants import Constants
from gamedata_parser import *
import numpy as np

# A subclass of the GameProps specific to Pong.
class PongGameProps(GameProps):

    # Pong currently has  6 inputs (see convert_state_to_network()) and 5 outputs (slow/fast up, slow/fast down, nothing)

    def __init__(self):
        self.pong_input_length = Constants.NUM_FRAMES_PER_STATE * 4
        super(PongGameProps, self).__init__(Games.PONG, self.pong_input_length, 3) # 3 actions: up, down, and stand still

        self.learning_rate = 1e-4

        self.experience_buffer_size = 100000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 1000

        # Slowly make agent less random
        self.num_steps_epislon_decay = 100000
        self.epsilon_end =  0.05
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay

        # Pong should only need one smaller hidden layer
        self.num_hidden_layers = 2
        self.set_hidden_units_array([64, 64])

        # Dont think we need to adjust epsilon as training progresses
        self.finetune_epsilon_end = None
        self.finetune_num_steps_before_epsilon_end = None
        self.finetune_step_size = None

    # format the data like this: [p1score, p1pos, p2score, p2pos, ballx, bally] for each frame in the state
    def convert_state_to_network_input(self, state):
        input = np.zeros((self.pong_input_length))
        for i in range(state.get_num_frames()):
            data = PongGameData(state.get_frame(i))
            base_index = i * 4
            input[base_index+0] = data.get_paddle_y_pos(1)
            input[base_index+1] = data.get_paddle_y_pos(2)
            input[base_index+2] = data.get_ball_x_pos()
            input[base_index+3] = data.get_ball_y_pos()
        return input