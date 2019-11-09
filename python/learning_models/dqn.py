import random
from learning_models.learning_model import LearningModel
from nn_utils import NeuralNetworkUtils as NNUtils
from collections import deque
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

MAIN_NETWORK = "main_network"
TRAIN_NETWORK = "train_network"
UPDATE_TARGET_INTERVAL = 10000
DOUBLE_DQN = True

class DQN(LearningModel):

    # Initialize defaults for all of the variables
    def __init__(self, session, game_props, rewarder):
        super(DQN, self).__init__(session, game_props, rewarder)
        self.random_action_probability = 1
        self.experiences = deque()
        self.number_training_iterations = 0
        self.model = NeuralNetwork(MAIN_NETWORK, session, game_props.network_input_length,
                                   game_props.network_output_length, game_props.hidden_units_arr,
                                   game_props.learning_rate).build()
        self.target_model = NeuralNetwork(TRAIN_NETWORK, session, game_props.network_input_length,
                                   game_props.network_output_length, game_props.hidden_units_arr,
                                   game_props.learning_rate).build()
        self.session = session

    # DQN only needs one experience (which holds the prev state, prev action, and current state_
    def get_client_experience_memory_size(self):
        return 1

    # Trains the model one iteration (i.e. usually one mini batch)
    def train_model(self, training_sample):
        # We aren't actually using the training_sample directly. For DQN, we store it in the experience replay list.
        # At this point, the sample is the entire client's history, but we only need to the top-most experience for DQN
        self.experiences.append(training_sample[-1])

        # if we don't have enough observations as dictated by the hyperparameters, then don't do any training until we do
        if self.number_training_iterations > self.game_props.num_obs_before_training:
            # If we have too many experiences in the replay list, pop the oldest one
            if len(self.experiences) > self.game_props.experience_buffer_size:
                self.experiences.popleft()

            # Now, do the DQN algorithm. This consists of getting a random batch from the experience replay buffer,
            # and using each item's prev state, action, current action, and reward to train the q-value estimator
            experience_batch = self.get_sample_batch()
            prev_states, curr_states, actions, rewards = [], [], [], []
            for experience in experience_batch:
                prev_states.append(self.convert_to_network_input(experience.prev_state))
                curr_states.append(self.convert_to_network_input(experience.curr_state))
                actions.append(NNUtils.get_one_hot(experience.prev_action, self.game_props.network_output_length))
                rewards.append(self.rewarder.calculate_reward(experience))

            self.train_neural_networks(experience_batch, prev_states, curr_states, actions, rewards)

            # Finally, update the probability of taking a random action according to epsilon
            if self.game_props.anneal_epsilon and self.random_action_probability > self.game_props.epsilon_end:
                self.random_action_probability -= self.game_props.epsilon_step_size

        self.number_training_iterations += 1

        if self.number_training_iterations % 10000 == 0:
            self.verbose_log_dump()

    def train_neural_networks(self, experience_batch, prev_states, curr_states, prev_actions, rewards):
        # Every N iterations, update the training network with the model of the "real" network
        if self.number_training_iterations % UPDATE_TARGET_INTERVAL == 0:
            copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, TRAIN_NETWORK)
            self.session.run(copy_ops)

        target_nn = self.target_model
        main_nn = self.model
        qvals = target_nn["output"].eval(feed_dict={target_nn["x"]: curr_states})
        theoretical_next_actions = None
        if DOUBLE_DQN:
            theoretical_next_actions = [np.argmax(x) for x in main_nn["output"].eval(feed_dict={main_nn["x"]: curr_states})]

        # Calculate the reward for each experience in the batch
        ybatch = []
        for i in range(len(experience_batch)):
            target = None
            # If the state is terminal, give the bot the reward for the state
            if self.rewarder.experience_is_terminal(experience_batch[i]):
                ybatch.append(rewards[i])

            # Otherwise, collect the reward plus the reward for the best action (multiplied by the future discount)
            else:
                discount = self.game_props.future_reward_discount
                discounted_reward = rewards[i] + (discount * np.amax(qvals[i]))
                # If using double DQN, don't take the max qval. Instead, take the best action from the main online model
                # and use that action's qval (produced by the target network)
                if DOUBLE_DQN:
                    target_qval = qvals[i][theoretical_next_actions[i]]
                    discounted_reward = rewards[i] + (discount * target_qval)

                ybatch.append(discounted_reward)

        # Learn that the previous states/actions led to the calculated rewards
        self.session.run(main_nn["train"], feed_dict={
            main_nn["x"] : prev_states,
            main_nn["action"] : prev_actions,
            main_nn["actual_q_value"] : ybatch
        })

    def convert_to_network_input(self, state):
        return self.game_props.convert_state_to_network_input(state)

    # Returns an action. Based on the 3rd arg, the action is either random, or taken from the learned policy
    def get_action(self, game_data, is_training=True):
        # Get a random action if we're training, and the random_action_probability calls for it
        if is_training and random.random() <= self.random_action_probability:
            return NNUtils.get_random_action(self.game_props.network_output_length)
        else:
            # Otherwise, get an action from the policy
            network_input = self.game_props.convert_state_to_network_input(game_data.get_current_state())
            q_vals_per_action = self.model["output"].eval(feed_dict={self.model["x"]: [network_input]})[0]
            return np.argmax(q_vals_per_action)

    # Returns a sample batch to train on.
    def get_sample_batch(self):
        num_samples = self.game_props.mini_batch_size
        num_total_experiences = len(self.experiences)
        if num_total_experiences < self.game_props.mini_batch_size:
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)

    def verbose_log_dump(self):
        print("\n***Verbose Log Dump*** ")
        print("Num Training Iterations: "+str(self.number_training_iterations))
        print("RANDOM PROB: "+str(self.random_action_probability))