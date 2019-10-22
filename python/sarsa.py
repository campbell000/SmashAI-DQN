# This class is responsible for the majority of our implementation of the DQN algorithm

import numpy as np
import tensorflow as tf
from collections import deque
import random
from reward import Rewarder
from gamedata_parser import *
from evaluator import Evaluator
from nn import NeuralNetwork
from shared_constants import Constants
import nn as NN
from nn_utils import NeuralNetworkUtils as NNUtils
import os
import uuid
from utils import Logger
from gameprops.gameprops import *
import datetime
import time
MAIN_NETWORK = "main"
TARGET_NETWORK = "target"
UPDATE_TARGET_INTERVAL = 10000
DOUBLE_DQN = True

class SarsaLearner:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, gameprops, rewarder, verbose=False):
        self.verbose = verbose
        self.rewarder = rewarder
        self.gameprops = gameprops
        self.session = session

        # Build the NN models (idiot)
        self.session.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.reward_log_path = "./reward_log.txt"
        self.probability_of_random_action = 1.0
        gameprops.dump()

    # Given a state, gets an action. Optionally, it also trains the Q-network if we are training (i.e. do_train=true)
    def get_prediction(self, game_data, do_train):
        if do_train:
            # do training
            a = 1

        return self.get_action(game_data)

    # Returns an action. Based on the 2nd arg, the action is either random, or taken from the learned policy
    def get_action(game_data, number_of_actions, random_action_probability):
        # Get a random action if the random_action_probability calls for it
        if random.random() <= random_action_probability:
            return get_random_action(number_of_actions)

    def get_random_action(number_of_actions):
        return random.randint(0,(number_of_actions - 1))

