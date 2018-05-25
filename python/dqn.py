# This class is responsible for the majority of our implementation of the DQN algorithm

import numpy as np
import tensorflow as tf
from collections import deque
import random
from reward import Rewarder
from evaluator import Evaluator
from nn import NeuralNetwork
from shared_constants import Constants
import nn as NN
from nn_utils import NeuralNetworkUtils as NNUtils
import os
import uuid
from utils import Logger

# Network-related constants
LEARNING_RATE = .00001
NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
INPUT_LENGTH = (Constants.NUM_FRAMES_PER_STATE * (NUM_POSSIBLE_STATES + 13) * 2) # taken from number of non-state params in client data, multiplied by 2 players
OUTPUT_LENGTH = 54 # taken from actions taken from gameConstants.lua
NUM_HIDDEN_UNITS = (INPUT_LENGTH * .6666) + OUTPUT_LENGTH # based on https://stats.stackexchange.com/questions/181/how-to-choose-the-number-of-hidden-layers-and-nodes-in-a-feedforward-neural-netw
NUM_HIDDEN_UNITS_2 = NUM_HIDDEN_UNITS / 2
HIDDEN_UNITS = [NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS_2]
NUM_LAYERS = 2

# DQN constants
EXPERIENCE_BUFFER_SIZE = 200000
FUTURE_REWARD_DISCOUNT = 0.95  # decay rate of past observations
MINI_BATCH_SIZE = 32  # size of mini batches
NUM_OBSERVATIONS_BEFORE_TRAINING = 1000
EPSILON_END = 0.05
NUM_STEPS_FOR_EPSILON_DECAY = 100000
EPSILON_DECAY_EXP = 0.98
EPSILON_STEP_SIZE = (1 - EPSILON_END) / NUM_STEPS_FOR_EPSILON_DECAY #

MAIN_NETWORK = "main"
TRAIN_NETWORK = "TRAIN"

#     def __init__(self, name, session, input_length, output_length,learning_rate, is_training=True, dropout_rate=0.05):
#
#

class SSB_DQN:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, verbose=False):
        self.rewarder = Rewarder(Constants.NUM_FRAMES_PER_STATE)
        self.experiences = deque()
        self.current_random_action_prob = 1
        self.evaluator = Evaluator(self.rewarder)
        self.print_once_map = {}
        self.num_iterations = 0
        self.model = NeuralNetwork(MAIN_NETWORK, session, INPUT_LENGTH, OUTPUT_LENGTH, LEARNING_RATE).build_model()
        self.target_model = NeuralNetwork(TRAIN_NETWORK, session, INPUT_LENGTH, OUTPUT_LENGTH, LEARNING_RATE).build_model()
        self.sess = session
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.saved_network_id = str(uuid.uuid4())
        self.logger = Logger(verbose)
        #self.saver = tf.train.import_meta_graph("./ac48aea8-8f33-4054-a700-3a23a331eda7-1000000.meta")
        #self.saver.restore(self.sess, tf.train.latest_checkpoint("./12-10-911/"))
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    # Given a state, gets an action. Optionally, it also trains the Q-network if we are training (i.e. do_train=true)
    def get_prediction(self, game_data, do_train):
        self.logger.log_once("Got Connection, Started Training!")

        # If training, record the experience and do some training (yo)
        if do_train:
            self.record_experience(game_data)
            self.train(game_data)

        # Get the action to send back to the client based on the current state
        action = self.get_action(game_data)

        # Update the probability that we're going to perform a random action
        self.update_random_prob()

        return action

    def update_random_prob(self):
        if self.current_random_action_prob > EPSILON_END:
            self.current_random_action_prob -= EPSILON_STEP_SIZE

    def get_action(self, game_data):
        # Choose either a random action, or an action produced by the network, based on chance
        action = np.zeros(OUTPUT_LENGTH)
        if random.random() <= self.current_random_action_prob:
            random_action_id = random.randint(0,(OUTPUT_LENGTH - 1))
            action[random_action_id] = 1
            return action
        else:
            # Prepare the current state's data as inputs into the network, and then get the network's output
            tf_current_state = NNUtils.prepare_data_for_network(game_data.get_current_state())
            output = self.model["output"].eval(feed_dict={self.model["x"]: [tf_current_state]})[0]
            action_index = np.argmax(output)
            action[action_index] = 1
            return action

    def record_experience(self, new_game_data):
        self.num_iterations +=1
        self.experiences.append(new_game_data)
        # if the number of iterations exceeds the buffer size, then we know that the buffer is full. pop the oldest entry.
        # TODO: potential problem if running multiple clients
        if self.num_iterations >= EXPERIENCE_BUFFER_SIZE:
            self.experiences.popleft()

    def train(self, game_data):
        if self.num_iterations > NUM_OBSERVATIONS_BEFORE_TRAINING:
            # Get the previous state, previous action, and rewards for the training process
            batch = self.get_sample_batch()
            previous_states = [NNUtils.transform_client_data_for_tensorflow(batch.get_previous_state, NUM_POSSIBLE_STATES)]
            previous_actions_taken = [NNUtils.get_one_hot(x) for x in sorted(batch.get_current_state().get_frames()[0]["prev_action_taken"])]
            rewards = [self.rewarder.calculate_reward(x) for x in batch]

            # TODO DO SOMETHING
            for i in range(len(batch)):
                # If the state is terminal (bot died)



    def get_sample_batch(self):
        num_samples = MINI_BATCH_SIZE
        num_total_experiences = len(self.experiences)
        if num_total_experiences < MINI_BATCH_SIZE:
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)


