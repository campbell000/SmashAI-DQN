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
from gameprops.mario_tennis_screenshot_gameprops import *
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
MARIOTENNIS_SCREENSHOT = 5

# Models
SARSA_MODEL = 0
DQN_MODEL = 1

# Dictates whether or not the training happens ONLY when a client asks for an action, or whether training happens
# on a separate thread
ASYNC_TRAINING = True
DUELING_DQN = False

USE_SAVED_MODEL = True
MODEL_TO_LOAD = "checkpoints/yoshi-yoshi-BIG-self-train-round1.ckpt"
CHECKPOINT_DIR_TO_LOAD = "checkpoints/"
MODEL_TO_SAVE_AS_NEW = "checkpoints/yoshi-yoshi-BIG-self-train-round2.ckpt"

# Variables for self-play training
DO_SELF_PLAY = True

# Variables to change to modify crucial hyper parameters (i.e. game being tested, DRL algorithm used, etc)
# Change this to modify the game
CURRENT_GAME = MARIOTENNIS_SCREENSHOT
MODEL = DQN_MODEL

# This class handles requests from bizhawk
class QuickOneMinuteOatsServer(BaseHTTPRequestHandler):
    rl_agent = None

    # This function handles requests from the client.
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length).decode() # <--- Gets the data itself
        game_data = GameDataParser.parse_client_data(data) # Parse the data into a map
        client_id = game_data.get_clientID()

        # If the action is TRAIN, get a best action, store the current state, and do some training (if we're doing sync training)
        if game_data.get_client_action() == TRAIN:
            print("TRAIN")
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

def start_learning_server(rl_agent):
    print('starting server...')

    # Run Server
    server_address = ('0.0.0.0', PORT)
    QuickOneMinuteOatsServer.rl_agent = rl_agent

    httpd = HTTPServer(server_address, QuickOneMinuteOatsServer)
    print("Now listening on "+str(PORT))
    httpd.serve_forever()
