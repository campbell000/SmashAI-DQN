from gameprops.gameprops import *
from shared_constants import Constants
from shared_constants import SharedConstants
from gamedata_parser import *
import numpy as np
import imageio
from PIL import Image
from io import BytesIO
import base64

# A subclass of the GameProps specific to Pong.
class MarioTennisScreenshotGameProps(GameProps):

    def __init__(self):
        IMAGE_WIDTH = 320
        IMAGE_HEIGHT = 240
        self.img_scaling_factor = 3
        shared_props = SharedConstants()
        self.num_frames_per_state = shared_props.get_prop_val('mario_tennis_screenshot', 'num_frames_per_state')
        self.network_input_length = (IMAGE_HEIGHT * self.num_frames_per_state, IMAGE_WIDTH, 3)
        self.preprocessed_input_length = (int(IMAGE_HEIGHT/self.img_scaling_factor) * self.num_frames_per_state,
                                          int(IMAGE_WIDTH/self.img_scaling_factor)  * self.num_frames_per_state, 3)
        self.network_output_length = 19
        super(MarioTennisScreenshotGameProps, self).__init__(self.network_input_length, self.network_output_length)

        self.do_grayscale = False # Need color for ball hit trails (slice, topspin, slam, etc)
        self.learning_rate = 1e-5
        self.experience_buffer_size = 50000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 32
        self.num_obs_before_training = 10000
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 1000000
        self.epsilon_end =  0.1
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.hidden_units_arr = [1024, 1024, 512]

        # Second schedule so that it goes from 1 to 0.1 in 4,000,000, and then from 0.1 to 0.01 in 1,000,000
        self.second_num_steps_epislon_decay = 1000000
        self.second_epsilon_end = 0.01
        self.second_epsilon_step_size = (self.epsilon_end - self.second_epsilon_end) / self.second_num_steps_epislon_decay
        self.cnn_params = [
            [64, 4, 4],
            [32, 4, 2],
            [16, 3, 1]
        ]

    def is_conv(self):
        return True

    def get_conv_params(self):
        return self.cnn_params

    def convert_state_to_network_input(self, state, reverse=False):
        input = []
        for i in range(state.get_num_frames()):
            data = state.get_frame(i)
            cleaned_image_data = data.get("image").strip('\n').strip('\r').replace(' ', '+')
            image = Image.open(BytesIO(base64.b64decode(cleaned_image_data + "==="))) # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
            image_array = np.asarray(image)
            if len(input) == 0:
                input = image_array
            else:
                input = np.vstack((input, image_array))
        return input