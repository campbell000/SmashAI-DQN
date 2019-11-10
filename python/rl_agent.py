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
from collections import deque
import queue
import copy

class RLAgent:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, gameprops, rewarder, model, client_memory_size=None, verbose=False):
        self.verbose = verbose
        self.rewarder = rewarder
        self.gameprops = gameprops
        self.session = session
        self.model = model
        self.sample_queue = queue.Queue(maxsize=1000)
        self.client_experience_queue = {}
        self.single_client_id = None
        self.model = model

        # The length of the client's history to record is dictated by the model if not specified.
        self.client_experience_memory_len = model.get_client_experience_memory_size() if client_memory_size is None else client_memory_size

        # Build the NN models (idiot)
        self.session.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        gameprops.dump()

    # Given a state, gets an action.
    def get_prediction(self, game_data, is_training=True):
        return self.model.get_action(game_data, is_training)

    # Stores the experience. It first stores the new data into a client-specific experience history. Then, if we're
    # doing async training, we add the current client history to the training sample queue (the trainer MAY not need
    # the full history (i.e. DQN just needs the most recent experience), but we're including it for ones that do (i.e. SARSA)
    def store_experience(self, client_id, current_state, action, async_training=True):
        # If this is the first time we're seeing this client, create a list to store experiences for that client
        experience = None
        add_to_training_queue = True
        if client_id not in self.client_experience_queue:
            self.client_experience_queue[client_id] = deque()
            experience = Experience(current_state, action, current_state, action) # create a "dummy" state just to make things simple for the first time
            add_to_training_queue = False
        else:
            # Create a NEW experience based off the prev state and prev action
            prev_exp = self.client_experience_queue[client_id][-1]
            experience = Experience(prev_exp.curr_state, prev_exp.curr_action, current_state, action)

        # TODO: uncomment to see the current action's reward
        #print("Current Reward: "+str(self.rewarder.calculate_reward(experience)))

        # Store the client's experience, but ensure that each client's history is limited
        client_memory = self.client_experience_queue[client_id]
        client_memory.append(experience)
        if len(client_memory) > self.client_experience_memory_len:
            client_memory.popleft()

        # Finally, copy the entire client's history (so we can continue to make changes to it) and put it on the
        # queue to be processed by the training algorithm. If the queue is full, drop training sample
        mem_copy = copy.deepcopy(client_memory)
        if add_to_training_queue and async_training:
            if not self.sample_queue.full():
                self.sample_queue.put_nowait(mem_copy)
            else:
                print("Dropping experience!")

        if not async_training:
            self.single_client_id = client_id

    # Trains the agent based on the given model
    def train_model(self, async_training=True):
        # If we're asynchronously training, grab the client's history from the sample queue (or wait until one exists)
        # Otherwise, just grab what's in the client's history directly (since we know it won'y be changing out from under us,
        # as we're doing synchronous training). TODO: This assumes that sync training = only one client!
        if async_training:
            self.model.train(self.sample_queue.get())
        else:
            self.model.train_model(self.client_experience_queue[self.single_client_id])

class Experience:
    def __init__(self, prev_state, prev_action, curr_state, curr_action):
        self.prev_state = prev_state
        self.prev_action = prev_action
        self.curr_state = curr_state
        self.curr_action = curr_action

    def get_prev_state(self):
        return self.prev_state

    def get_curr_state(self):
        return self.curr_state

