import numpy as np
from collections import deque
import random
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
import datetime
import multiprocessing

PREDICTION_UPDATE_INTERVAL = 1000

class RLAgent:
    def __init__(self, rewarder, model_trainer, model_predictor, verbose=False):
        self.verbose = verbose
        self.rewarder = rewarder
        self.model_trainer = model_trainer
        self.model_predictor = model_predictor
        self.client_experience_queue = {}
        self.single_client_id = None
        self.screenshot_dict = {}

        # Used for logging peformance
        self.predictions_asked_for = 0
        self.average_reward_interval = 20000
        self.reward_sum = 0
        self.dropped = 0

        # The length of the client's history to record is dictated by the model if not specified.
        self.client_experience_memory_len = 1 # TODO SHOULD COME FROM ALGORITHM IMPLEMENTATION

    # Given a state, gets an action.
    def get_prediction(self, game_data, is_training=True, is_for_self_play=False):
        if not is_for_self_play:
            self.predictions_asked_for = self.predictions_asked_for + 1

        if self.predictions_asked_for % 1000 == 0:
            self.model_predictor.refresh_predictor(self.model_trainer)

        return self.model_predictor.get_action(game_data, is_training, is_for_self_play=is_for_self_play)

    # Stores the experience. It first stores the new data into a client-specific experience history. Then, if we're
    # doing async training, we add the current client history to the training sample queue (the trainer MAY not need
    # the full history (i.e. DQN just needs the most recent experience), but we're including it for ones that do (i.e. SARSA)
    def train_with_current_experience(self, client_id, current_state, action):
        if current_state.get_num_frames() < Constants.NUM_FRAMES_PER_STATE:
            print("DROPPING EXPERIENCE because the number of frames is wrong")
            return

        # If this is the first time we're seeing this client, create a list to store experiences for that client
        experience = None
        has_valid_training_sample = True
        if client_id not in self.client_experience_queue:
            self.client_experience_queue[client_id] = deque()
            experience = Experience(current_state, action, current_state, action) # create a "dummy" state just to make things simple for the first time
            has_valid_training_sample = False
            print("Just met "+str(client_id))
        else:
            # Create a NEW experience based off the prev state and prev action
            prev_exp = self.client_experience_queue[client_id][-1]
            experience = Experience(prev_exp.curr_state, prev_exp.curr_action, current_state, action)

        # TODO: uncomment to see the current action's reward
        experience.reward = self.rewarder.calculate_reward(experience)
        experience.is_terminal = self.rewarder.experience_is_terminal(experience)
        #print("Current Reward: "+str(experience.reward)+" AND IS TERMINAL: "+str(experience.is_terminal))

        # Store the client's experience, but ensure that each client's history is limited
        client_memory = self.client_experience_queue[client_id]
        client_memory.append(experience)
        if len(client_memory) > self.client_experience_memory_len:
            client_memory.popleft()

        # Finally, copy the entire client's history (we treat the current history as a discrete training sample) and put it on the
        # queue to be processed by the training algorithm. If the queue is full, drop training sample
        mem_copy = copy.deepcopy(client_memory)
        if has_valid_training_sample:
            self.model_trainer.train_model(mem_copy)

        self.log_average_reward(experience)

    def log_average_reward(self, experience):
        reward = self.rewarder.calculate_reward(experience)
        self.reward_sum = self.reward_sum + reward
        if self.predictions_asked_for % self.average_reward_interval == 0:
            datestr = datetime.datetime.now()
            average_reward = self.reward_sum / self.average_reward_interval
            self.reward_sum = 0
            row = "\""+str(datestr)+"\", \""+str(self.predictions_asked_for)+"\", \""+str(average_reward)+"\""
            with open("reward_logs.txt", "a+") as file:
                file.write(row+"\n")

    # Trains the agent based on the given model
    def train_model(self):
        self.model.train_model(self.sample_queue.get())

class Experience:
    def __init__(self, prev_state, prev_action, curr_state, curr_action):
        self.prev_state = prev_state
        self.prev_action = prev_action
        self.curr_state = curr_state
        self.curr_action = curr_action
        self.reward = -999
        self.is_terminal = -999

    def get_prev_state(self):
        return self.prev_state

    def get_curr_state(self):
        return self.curr_state


