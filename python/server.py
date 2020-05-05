# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot.

PORT = 8081
from http.server import BaseHTTPRequestHandler, HTTPServer
import tensorflow as tf
from gamedata_parser import GameDataParser
from gameprops.gameprops import *
from gameprops.pong_gameprops import *
from gameprops.ssb_gameprops import *
from gameprops.mario_tennis_gameprops import *
from gameprops.pong_screenshot_gameprops import *
from shared_constants import Constants
from gamedata_parser import *
from rewarder.rewarder import *
from rewarder.pong_rewarder import *
from rewarder.pong_screenshot_rewarder import *
from rewarder.ssb_rewarder import *
from rewarder.dumb_ssb_rewarder import *
from rewarder.mario_tennis_rewarder import *
from learning_models.dqn import DQN
from rl_agent import RLAgent
from rewarder.rewarder import *
import threading

# THESE VARIABLES SHOULD MATCH THE VARIABLES IN tensorflow-client.lua
TRAIN = 0
EVAL = 1
HELLO = 2
CLIPBOARD_SCREENSHOT = 3
TRAIN_SELF_PLAY = 4

# Variables for games
SMASH = 0
PONG = 1
MARIOTENNIS = 2
TESTING = 3
PONG_SCREENSHOT = 4

# Models
SARSA_MODEL = 0
DQN_MODEL = 1

# Dictates whether or not the training happens ONLY when a client asks for an action, or whether training happens
# on a separate thread
ASYNC_TRAINING = True
DUELING_DQN = False
USING_CLIPBOARD_SCREENSHOTS = False

USE_SAVED_MODEL = True
MODEL_TO_LOAD = "checkpoints/yoshi-yoshi-BIG-self-train-round1.ckpt"
CHECKPOINT_DIR_TO_LOAD = "checkpoints/"
MODEL_TO_SAVE_AS_NEW = "checkpoints/yoshi-yoshi-BIG-self-train-round2.ckpt"

# Variables for self-play training
DO_SELF_PLAY = True

# Variables to change to modify crucial hyper parameters (i.e. game being tested, DRL algorithm used, etc)
# Change this to modify the game
CURRENT_GAME = SMASH
MODEL = DQN_MODEL

# This class handles requests from bizhawk
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    rl_agent = None
    started = False

    # This function handles requests from the client.
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length).decode() # <--- Gets the data itself
        game_data = GameDataParser.parse_client_data(data) # Parse the data into a map
        client_id = game_data.get_clientID()

        if game_data.get_client_action() == CLIPBOARD_SCREENSHOT:
            self.rl_agent.store_screenshot_for_client_from_clipboard(game_data.get_clientID())
            response = "OK"

        # If the action is TRAIN, get a best action, store the current state, and do some training (if we're doing sync training)
        elif game_data.get_client_action() == TRAIN:
            print("TRAIN")
            # If doing screenshots, we are sending ONLY the stuff we need to calculate reward. And we're ONLY
            # sending values for ONE frame. We need to gather all the screenshots and add them to the game_data objects
            if USING_CLIPBOARD_SCREENSHOTS:
                self.rl_agent.store_screenshot_for_client_from_clipboard(client_id)
                GameDataParser.add_screenshots_to_gamedata(game_data, self.rl_agent.get_screenshot_buffer_for_client(client_id, clear=True))

            action = self.rl_agent.get_prediction(game_data, is_training=True)
            self.rl_agent.store_experience(client_id, game_data.get_current_state(), action, async_training=ASYNC_TRAINING)
            if not ASYNC_TRAINING:
                self.rl_agent.train_model(async_training=ASYNC_TRAINING)

            response = str(action)

        # If we're self training, return TWO actions. Return one action for the model that's actually training,
        # and another that ISNT training, and has an earlier version of the model
        elif game_data.get_client_action() == TRAIN_SELF_PLAY:
            action = self.rl_agent.get_prediction(game_data, is_training=True)
            self_play_action = self.rl_agent.get_prediction(game_data, is_training=False, is_for_self_play=True)
            self.rl_agent.store_experience(client_id, game_data.get_current_state(), action, async_training=ASYNC_TRAINING)
            if not ASYNC_TRAINING:
                self.rl_agent.train_model(async_training=ASYNC_TRAINING)

            response = str(action)+","+str(self_play_action)
        elif game_data.get_client_action() == EVAL:
            action = self.rl_agent.get_prediction(game_data, is_training=False)
            response = str(action)
        else:
            print("Saying HELLO to the tensorflow client!")
            response = "HI FROM TENSORFLOW SERVER! THIS IS WHAT YOU SENT ME:\n"+str(data)

        # Write the response of the action to the client
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(response, "utf8"))

    # Silences logging
    def log_message(self, format, *args):
        return

def transform_actions_for_client(action_arr):
    str_int_array = (str(int(e)) for e in action_arr)
    return ','.join(str_int_array)

def run():
    print('starting server...')
    config = tf.ConfigProto()
    config.gpu_options.allow_growth=True
    if not USE_SAVED_MODEL:
        print("Initializing random weights")
        tf.variance_scaling_initializer(scale=2)
    else:
        print("Skipping weight init due to saved model being used")
    sess = tf.Session(config=config)

    with sess.as_default():
        props = get_game_specific_params()

        # Run Server
        server_address = ('0.0.0.0', PORT)
        model = get_learning_model(sess, props[0], props[1])
        testHTTPServer_RequestHandler.rl_agent = RLAgent(sess, props[0], props[1], model)
        do_post_init(props[0], testHTTPServer_RequestHandler.rl_agent, sess)
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')

        # If async training, then spawn an endless loop that trains the model when experiences have been placed in the
        # queue
        if ASYNC_TRAINING:
            print("Starting async training thread!")
            thread = threading.Thread(target=async_training, args=(sess, tf.get_default_graph(),))
            thread.daemon = True
            thread.start()

        httpd.serve_forever()

def async_training(sess, g):
    with g.as_default():
        varsToRestore = tf.contrib.slim.get_variables_to_restore()
        variables_to_restore = [v for v in varsToRestore if v.name.split('/')[0]=='main_network']
        saver = tf.train.Saver(variables_to_restore, max_to_keep=1)
        testHTTPServer_RequestHandler.rl_agent.set_saver(saver, MODEL_TO_SAVE_AS_NEW)
        if USE_SAVED_MODEL:
            print("**** USING SAVED MODEL: "+MODEL_TO_LOAD+" *******")
            saver = tf.train.import_meta_graph(MODEL_TO_LOAD+".meta")
            saver.restore(sess,tf.train.latest_checkpoint(CHECKPOINT_DIR_TO_LOAD))
            print("**** DONE LOADING! ******")

        if DO_SELF_PLAY:
            print("Initializing self play network with main networks")
            testHTTPServer_RequestHandler.rl_agent.init_self_play()
            print("Done init self play network")

        while True:
            testHTTPServer_RequestHandler.rl_agent.train_model()

# Returns the current game's hyper parameters and reward function
def get_game_specific_params():
    if CURRENT_GAME == PONG:
        return [PongGameProps(), PongRewarder()]
    if CURRENT_GAME == PONG_SCREENSHOT:
        return [PongScreenshotGameProps(), PongScreenshotRewarder()]
    elif CURRENT_GAME == SMASH:
        return [SSBGameProps(), SSBRewarder()]
    elif CURRENT_GAME == MARIOTENNIS:
        return [MarioTennisGameprops(), MarioTennisRewarder()]
    elif CURRENT_GAME == TESTING:
        print("AGHHHH")

# Returns the current game's hyper parameters and reward function
def do_post_init(gameprops, rl_agent, session):
    if CURRENT_GAME == PONG:
        return
    if CURRENT_GAME == PONG_SCREENSHOT:
        gameprops.session = session
        gameprops.model = rl_agent.model.get_model()
    elif CURRENT_GAME == SMASH:
        return
    elif CURRENT_GAME == MARIOTENNIS:
        return
    elif CURRENT_GAME == TESTING:
        print("AGHHHH")

# Returns the current learning model (i.e. DQN, SARSA, etc)
def get_learning_model(sess, gameprops, rewarder):
    if MODEL == DQN_MODEL:
        print("Building DQN model. Dueling: "+str(DUELING_DQN))
        return DQN(sess, gameprops, rewarder, DUELING_DQN, is_self_play=DO_SELF_PLAY)

run()
