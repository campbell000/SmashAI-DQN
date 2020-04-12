# Run this file to start the server and the machine learning model. Change constants here to change the game being
# played, as well as other parameters.

# TODO: probably should be command-line driven, but I primarily run this stuff from IntelliJ IDE, and command-line
# arguments are really, really annoying to configure in it.

import server
from server import *
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
ASYNC_TRAINING = True

CURRENT_GAME = PONG
MODEL = DQN_MODEL

MODEL_STRING = "DQN" if MODEL == DQN_MODEL else "SARSA"
GAME_STRING = None
if CURRENT_GAME == PONG:
    GAME_STRING = "PONG"
elif CURRENT_GAME == PONG_SCREENSHOT:
    GAME_STRING = "PONG_SCREENSHOT"
elif CURRENT_GAME == MARIOTENNIS:
    GAME_STRING = "MARIO_TENNIS"
elif GAME_STRING == MARIOTENNIS_SCREENSHOT:
    GAME_STRING = "MARIOTENNIS_SCREENSHOT"
elif CURRENT_GAME == SMASH:
    GAME_STRING = "SUPER_SMASH_BRUDDAS"

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
        model = get_learning_model(sess, props[0], props[1])
        rl_agent = RLAgent(sess, props[0], props[1], model)
        do_post_init(props[0], rl_agent, sess)

        # If async training, then spawn an endless loop that trains the model when experiences have been placed in the
        # queue
        if ASYNC_TRAINING:
            print("Starting async training thread!")
            thread = threading.Thread(target=async_training, args=(rl_agent, sess, tf.get_default_graph(),))
            thread.daemon = True
            thread.start()

        start_learning_server(rl_agent)

def async_training(rl_agent, sess, g):
    with g.as_default():
        varsToRestore = tf.contrib.slim.get_variables_to_restore()
        variables_to_restore = [v for v in varsToRestore if v.name.split('/')[0]=='main_network']
        saver = tf.train.Saver(variables_to_restore, max_to_keep=1)
        rl_agent.set_saver(saver, MODEL_TO_SAVE_AS_NEW)
        if USE_SAVED_MODEL:
            print("**** USING SAVED MODEL: "+MODEL_TO_LOAD+" *******")
            saver = tf.train.import_meta_graph(MODEL_TO_LOAD+".meta")
            saver.restore(sess,tf.train.latest_checkpoint(CHECKPOINT_DIR_TO_LOAD))
            print("**** DONE LOADING! ******")

        if DO_SELF_PLAY:
            print("Initializing self play network with main networks")
            rl_agent.init_self_play()
            print("Done init self play network")

        while True:
            rl_agent.train_model()

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
def get_learning_model(sess, gameprops, rewarder):
    if MODEL == DQN_MODEL:
        print("Building DQN algorithm implementation. Dueling: "+str(DUELING_DQN))
        return DQN(sess, gameprops, rewarder, DUELING_DQN, is_self_play=DO_SELF_PLAY)

def dump_main():
    print("Dump from main: ")
    print("MODEL: "+MODEL_STRING)
    print("GAME: "+GAME_STRING)

if __name__ == '__main__':
    dump_main()
    run()