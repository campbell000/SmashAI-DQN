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
from gameprops.gameprops import *

MAIN_NETWORK = "main"
TRAIN_NETWORK = "TRAIN"
UPDATE_TARGET_INTERVAL = 2000

class SSB_DQN:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, gameprops, rewarder, verbose=False):
        self.verbose = verbose
        self.rewarder = rewarder
        self.gameprops = gameprops
        self.experiences = deque()
        self.current_random_action_prob = 1
        self.evaluator = Evaluator(self.rewarder)
        self.print_once_map = {}
        self.num_iterations = 0
        self.model = NeuralNetwork(MAIN_NETWORK, session, gameprops.get_network_input_len(), gameprops.get_network_output_len(), gameprops.get_learning_rate()).build_model()
        self.target_model = NeuralNetwork(TRAIN_NETWORK, session, gameprops.get_network_input_len(), gameprops.get_network_output_len(), gameprops.get_learning_rate()).build_model()
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

        # Record some other things, like the reward for the current state
        if self.verbose:
            self.verbose_log_dump()

        return action

    def update_random_prob(self):
        if self.current_random_action_prob > self.gameprops.get_epsilon_end():
            self.current_random_action_prob -= self.gameprops.get_epsilon_step_size()

    def get_action(self, game_data):
        # Choose either a random action, or an action produced by the network, based on chance
        action = np.zeros(self.gameprops.get_network_output_len())
        if random.random() <= self.current_random_action_prob:
            self.logger.log_verbose("Chose random action "+str())
            random_action_id = random.randint(0,(self.gameprops.get_network_output_len() - 1))
            action[random_action_id] = 1
            self.logger.log_verbose("Chose random action "+str(random_action_id)+", random probability is "+str(self.current_random_action_prob))
            return action
        else:
            # Prepare the current state's data as inputs into the network, and then get the network's output
            network_input = self.gameprops.convert_state_to_network_input(game_data.get_current_state())
            output = self.model["output"].eval(feed_dict={self.model["x"]: [network_input]})[0]
            action_index = np.argmax(output)
            self.logger.log_verbose("Chose optimal action "+str(action_index)+", random probability is "+str(self.current_random_action_prob))
            action[action_index] = 1
            return action

    def record_experience(self, new_game_data):
        self.num_iterations +=1
        self.experiences.append(new_game_data)
        self.logger.log_verbose("Recording new Experience...has "+str(self.num_iterations)+" total")
        # if the number of iterations exceeds the buffer size, then we know that the buffer is full. pop the oldest entry.
        # TODO: potential problem if running multiple clients
        if self.num_iterations >= self.gameprops.get_experience_buffer_size():
            self.experiences.popleft()

    def train(self, game_data):
        target_nn = self.target_model
        training_nn = self.model

        # Train only if we've collected enough observations
        if self.num_iterations > self.gameprops.get_num_obs_before_training():
            batch = self.get_sample_batch()

            # Convert previous states for every experience in batch to inputs for the NN
            previous_states = [self.gameprops.convert_state_to_network_input(x.get_previous_state()) for x in batch]

            # Convert the previous actions taken (should be an integer) into a one-hot-encoded vector
            previous_actions_taken = [NNUtils.get_one_hot(x.get_current_state().get_frames()[0]["prev_action_taken"]) for x in batch]

            # Get current states, and the expected rewards (according to the Q-Network) for each action
            current_states = [self.gameprops.convert_state_to_network_input(x.get_current_state()) for x in batch]
            current_action_exp_rewards = target_nn["output"].eval(feed_dict={target_nn["x"]: current_states})

            # Calculate rewards for every experience in the batch
            rewards = [self.rewarder.calculate_reward(x) for x in batch]
            agent_exp_rewards = np.zeros((len(batch)))

            # Calculate the reward for each experience in the batch
            for i in range(len(batch)):
                # If the state is terminal (bot died), give the bot the reward for the state
                if self.rewarder.experience_is_terminal(batch[i]):
                    agent_exp_rewards[i] = rewards[i]

                # Otherwise, collect the reward plus the reward for the best action (multiplied by the future discount)
                else:
                    agent_exp_rewards[i] = (self.gameprops.get_future_reward_discount() * np.max(current_action_exp_rewards[i]))

            # Learn that the previous states/actions led to the calculated rewards
            training_nn["sess"].run(training_nn["train"], feed_dict={
                training_nn["x"] : previous_states,
                training_nn["action"] : previous_actions_taken,
                training_nn["target"] : agent_exp_rewards
            })

            # Every N iterations, update the training network with the model of the "real" network
            if self.num_iterations % UPDATE_TARGET_INTERVAL == 0:
                copy_ops = NNUtils.get_copy_var_ops(TRAIN_NETWORK, MAIN_NETWORK)
                self.sess.run(copy_ops)
        else:
            self.logger.log_verbose("Not yet training....not enough experiences")

    # Returns a sample batch to train on.
    def get_sample_batch(self):
        num_samples = self.gameprops.get_mini_batch_size()
        num_total_experiences = len(self.experiences)
        if num_total_experiences < self.gameprops.get_mini_batch_size():
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)

    def verbose_log_dump(self):
        print("HI")


