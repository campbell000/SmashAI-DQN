# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot.

import server
from server import *
import tensorflow as tf
from gamedata_parser import GameDataParser
from gameprops.gameprops import *
from model import *
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
from ml_algorithms.dqn import DQN
from rl_agent import RLAgent
from rewarder.rewarder import *
import threading
import multiprocessing

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
DUELING_DQN = False

USE_SAVED_MODEL = False
DO_SAVING = False
MODEL_TO_LOAD = "checkpoints/smash-mario-dk-level9.ckpt"
CHECKPOINT_DIR_TO_LOAD = "checkpoints/"
MODEL_TO_SAVE_AS_NEW = "checkpoints/yoshi-yoshi-BIG-level9.ckpt"

# Variables for self-play training
DO_SELF_PLAY = False

# Variables to change to modify crucial hyper parameters (i.e. game being tested, DRL algorithm used, etc)
# Change this to modify the game
CURRENT_GAME = PONG
MODEL = DQN_MODEL


def run_real():
    pipe = multiprocessing.Pipe()
    props = get_game_specific_params()
    model_trainer = MachineLearningModel(pipe[1], USE_SAVED_MODEL, props[0], props[1], MODEL, DO_SELF_PLAY,
                                         MODEL_TO_LOAD, CHECKPOINT_DIR_TO_LOAD, DO_SAVING)
    model_predictor = MachineLearningModel(pipe[1], USE_SAVED_MODEL, props[0], props[1], MODEL, DO_SELF_PLAY,
                                                  MODEL_TO_LOAD, CHECKPOINT_DIR_TO_LOAD, DO_SAVING)
    model_trainer.start()
    model_predictor.configure_model()

    rl_agent = RLAgent(props[1], model_trainer, model_predictor)
    start_learning_server(rl_agent)

# Returns the current game's hyper parameters and reward function
def get_game_specific_params():
    if CURRENT_GAME == PONG:
        return [PongGameProps(), PongRewarder()]
    if CURRENT_GAME == PONG_SCREENSHOT:
        return [PongScreenshotGameProps(), PongScreenshotRewarder()]
    if CURRENT_GAME == MARIOTENNIS_SCREENSHOT:
        return [MarioTennisScreenshotGameProps(), MarioTennisRewarder()]
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
        return
    elif CURRENT_GAME == SMASH:
        return
    elif CURRENT_GAME == MARIOTENNIS:
        return
    elif CURRENT_GAME == TESTING:
        print("AGHHHH")

# Returns the current learning algorithm (i.e. DQN, SARSA, etc)
def get_learning_algorithm(sess, gameprops, rewarder):
    if MODEL == DQN_MODEL:
        print("Building DQN algorithm implementation. Dueling: "+str(DUELING_DQN))
        return DQN(sess, gameprops, rewarder, DUELING_DQN, is_self_play=DO_SELF_PLAY)


if __name__ == '__main__':
    run_real()
    #run()
