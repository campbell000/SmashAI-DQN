from gameprops.gameprops import *
from shared_constants import Constants
from gamedata_parser import *
import numpy as np
#import imageio
#from PIL import Image
#import PIL
import uuid

# A subclass of the GameProps specific to Pong.
class PongScreenshotGameProps(GameProps):

    def __init__(self):
        # HARDCODED RESULTS OF SCREENSHOT CROPPING
        self.LEFT = 27
        self.TOP = 31
        self.RIGHT = 20
        self.BOTTOM = 14
        IMAGE_WIDTH = (320 - self.LEFT) - self.RIGHT
        IMAGE_HEIGHT = (240 - self.TOP) - self.BOTTOM

        self.pong_input_length = (IMAGE_HEIGHT * Constants.NUM_FRAMES_PER_STATE, IMAGE_WIDTH, 3)
        super(PongScreenshotGameProps, self).__init__(self.pong_input_length, 3) # 3 actions: up, down, and stand still
        self.cnn_params = [
            [32, 8, 4],
            [64, 4, 2],
            [64, 3, 1]
        ]
        self.hidden_units_arr = [512, 256]
        self.experience_buffer_size = 20000
        self.future_reward_discount = 0.95
        self.mini_batch_size = 16
        self.num_obs_before_training = 16

        # Slowly make agent less random
        self.anneal_epsilon = True
        self.num_steps_epislon_decay = 500000
        self.epsilon_end =  0.05
        self.epsilon_step_size = (1 - self.epsilon_end) / self.num_steps_epislon_decay
        self.img_scaling_factor = 3
        self.preprocessed_input_length = (int(IMAGE_HEIGHT/self.img_scaling_factor) * Constants.NUM_FRAMES_PER_STATE,
                                          int(IMAGE_WIDTH/self.img_scaling_factor), 1)
        self.model = None
        self.session = None

    def is_conv(self):
        return True

    def get_conv_params(self):
        return self.cnn_params

    def convert_state_to_network_input(self, state):
        input = []
        for i in range(state.get_num_frames()):
            data = state.get_frame(i)
            image = data.get("screenshot")
            w, h = image.size
            cropped = image.crop((self.LEFT, self.TOP, w - self.RIGHT, h - self.BOTTOM))
            image_array = np.asarray(cropped)
            if len(input) == 0:
                input = image_array
            else:
                input = np.vstack((input, image_array))


        with self.session.as_default():
            feed_dict = {self.model["rawInput"]: [input]}
            return self.model["grayscaled"].eval(feed_dict=feed_dict)[0]