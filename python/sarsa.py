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
"""
class SarsaLearner:
    def __init__(self, session, n_steps):
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
    def get_prediction(self, game_data):
        return self.get_action(game_data)

    # Returns an action. Based on the 3rd arg, the action is either random, or taken from the learned policy
    def get_action(self, game_data, number_of_actions, random_action_probability):
        # Get a random action if the random_action_probability calls for it
        if random.random() <= random_action_probability:
            return NNUtils.get_random_action(number_of_actions)
        else:
            # Otherwise, get an action from the policy
            return get_action_based_on_policy(game_data)

    def get_action_based_on_policy(self, game_data):
"""



