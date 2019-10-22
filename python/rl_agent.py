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
import queue

class RLAgent:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, gameprops, rewarder, model, client_experience_memory_size=1, verbose=False):
        self.verbose = verbose
        self.rewarder = rewarder
        self.gameprops = gameprops
        self.session = session
        self.model = model
        self.sample_queue = queue.Queue(maxsize=100)
        self.client_experience_queue = queue.Queue(maxsize=gameprops.get_client_experience_size())
        self.client_experience_memory_size = client_experience_memory_size

        # Build the NN models (idiot)
        self.session.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.reward_log_path = "./reward_log.txt"
        self.probability_of_random_action = 1.0
        gameprops.dump()

    # Given a state, gets an action. Optionally, it also trains the Q-network if we are training (i.e. do_train=true)
    def get_prediction(self, game_data):
        return self.get_action(game_data)

    def store_experience(self, client_id, current_state, action):
        experience = Experience(current_state, action)

    # Returns an action. Based on the 3rd arg, the action is either random, or taken from the learned policy
    def get_action(self, game_data, number_of_actions, random_action_probability):
        # Get a random action if the random_action_probability calls for it
        if random.random() <= random_action_probability:
            return NNUtils.get_random_action(number_of_actions)
        else:
            # Otherwise, get an action from the policy
            return self.model.get_best_action(game_data)

    def train_model(self):


class Experience:
    def __init__(self, current_state, action_taken_from_current_state):
        self.current_state = current_state
        self.action_taken_from_current_state = action_taken_from_current_state


