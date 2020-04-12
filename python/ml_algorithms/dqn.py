import random
from ml_algorithms.ml_algorithm import MLAlgorithm
from nn_utils import NeuralNetworkUtils as NNUtils
from collections import deque
import numpy as np
import tensorflow as tf
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
from cnn import ConvolutionalNeuralNetwork
from PIL import Image

MAIN_NETWORK = "main_network"
TRAIN_NETWORK = "train_network"
SELF_PLAY_NETWORK = "self_play"
UPDATE_TARGET_INTERVAL = 10000
UPDATE_SELF_PLAY_INTERVAL = 18000000
UPDATE_MODEL_PREDICTOR_VALS_INTERVAL = 1000
DOUBLE_DQN = True
import datetime

class DQN(MLAlgorithm):

    # Initialize defaults for all of the variables
    def __init__(self, pipe, session, game_props, rewarder, is_dueling, is_self_play=False, use_sorted_rewards=False):
        super(DQN, self).__init__(session, game_props, rewarder)
        self.pipe = pipe
        self.random_action_probability = 1
        self.experiences = deque()
        self.number_training_iterations = 0
        self.sorted_buffer = []
        self.use_sorted_rewards = use_sorted_rewards
        self.saver = None
        self.is_self_play = is_self_play
        self.saver_name = None
        self.model_predictor_vals = None
        if not game_props.is_conv():
            self.model = NeuralNetwork(MAIN_NETWORK, game_props.network_input_length, game_props.network_output_length,
                                       game_props.hidden_units_arr, game_props.learning_rate)
            self.target_model = NeuralNetwork(TRAIN_NETWORK, game_props.network_input_length, game_props.network_output_length,
                                              game_props.hidden_units_arr,game_props.learning_rate)
            if (self.is_self_play):
                self.self_play_model = NeuralNetwork(SELF_PLAY_NETWORK, game_props.network_input_length, game_props.network_output_length,
                                                      game_props.hidden_units_arr,game_props.learning_rate)

        else:
            self.model = ConvolutionalNeuralNetwork(MAIN_NETWORK, game_props.network_input_length, game_props.preprocessed_input_length, game_props.network_output_length,
                                       game_props.hidden_units_arr,game_props.get_conv_params(), game_props.learning_rate, game_props.mini_batch_size,
                                                    game_props.img_scaling_factor, do_grayscale=game_props.do_grayscale)
            self.target_model = ConvolutionalNeuralNetwork(TRAIN_NETWORK, game_props.network_input_length, game_props.preprocessed_input_length, game_props.network_output_length,
                                          game_props.hidden_units_arr,game_props.get_conv_params(), game_props.learning_rate, game_props.mini_batch_size,
                                                           game_props.img_scaling_factor, do_grayscale=game_props.do_grayscale)

        # If using Dueling DQN, build a NN that separates the value and advantage functions
        if is_dueling:
            print("IS DUELING!")
            self.model = self.model.build_dueling()
            self.target_model = self.target_model.build_dueling()
        else:
            self.model = self.model.build()
            self.target_model = self.target_model.build()
            if self.is_self_play:
                self.self_play_model = self.self_play_model.build()

        if self.use_sorted_rewards:
            print("USING SORTED REWARDS FOR SPARSE GAMES")


        self.session = session
        self.prioritized_replay = True

    # DQN only needs one experience (which holds the prev state, prev action, and current state)
    def get_client_experience_memory_size(self):
        return 1

    def get_model(self):
        return self.model

    def set_saver(self, saver, name):
        self.saver = saver
        self.saver_name = name

    def init_self_play_network(self):
        if self.is_self_play:
            with self.session.as_default():
                copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, SELF_PLAY_NETWORK)
                self.session.run(copy_ops)

    def reset_for_self_play_update(self):
        self.random_action_probability = 1
        self.experiences.clear()
        self.number_training_iterations = 0

    # Trains the model one iteration (i.e. usually one mini batch)
    def train_model(self, training_sample):
        # We aren't actually using the training_sample directly. For DQN, we store it in the experience replay list.
        # At this point, the sample is the entire client's history, but we only need to the top-most experience for DQN
        self.experiences.append(training_sample[-1])

        # Let people know that the training has started
        if len(self.experiences) == self.game_props.num_obs_before_training:
            print( self.game_props.num_obs_before_training)
            print("Started Training! Got "+str(len(self.experiences))+" experiences in experience replay")

        # if we don't have enough observations as dictated by the hyperparameters, then don't do any training until we do
        if len(self.experiences) > self.game_props.num_obs_before_training:
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
                rewards.append(experience.reward)

            #if self.number_training_iterations % 1000000 == 0 and self.number_training_iterations > 10:
            #    self.saver.save(self.session, self.saver_name)

            self.train_neural_networks(experience_batch, prev_states, curr_states, actions, rewards)

            # Finally, update the probability of taking a random action according to epsilon
            # TODO: Revisit this if planning to use multiple agents. We might want to decrease this probability
            # TODO: on getting actions, rather than every training sample.
            self.adjust_random_action_prob()

        self.number_training_iterations += 1

        if self.number_training_iterations % 10000 == 0:
            self.verbose_log_dump()

    def adjust_random_action_prob(self):
        if self.game_props.anneal_epsilon:
            if self.random_action_probability > self.game_props.epsilon_end:
                self.random_action_probability -= self.game_props.epsilon_step_size
            elif self.random_action_probability > self.game_props.second_epsilon_end:
                self.random_action_probability -= self.game_props.second_epsilon_step_size

    def init_self_play_networks(self):
        with self.session.as_default():
            copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, TRAIN_NETWORK)
            self.session.run(copy_ops)
            copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, SELF_PLAY_NETWORK)
            self.session.run(copy_ops)

    def train_neural_networks(self, experience_batch, prev_states, curr_states, prev_actions, rewards):
        # Every N iterations, update the training network with the model of the "real" network
        if self.number_training_iterations % UPDATE_TARGET_INTERVAL == 0:
            print("Updating target network...")
            copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, TRAIN_NETWORK)
            self.session.run(copy_ops)
            print("Done!");

        # Every M iterations, if we're self-playing, copy the main network into the self playing network
        if self.is_self_play and self.number_training_iterations % UPDATE_SELF_PLAY_INTERVAL == 0:
            print("Updating self player...")
            copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, SELF_PLAY_NETWORK)
            self.session.run(copy_ops)
            print("DONE!");
            self.reset_for_self_play_update()
            self.verbose_log_dump()

        # Every X iterations, update the cached set of values used to make predictions. Useful so that other processes
        # use a copy of the predictor network
        if self.number_training_iterations % UPDATE_MODEL_PREDICTOR_VALS_INTERVAL == 0:


        target_nn = self.target_model
        main_nn = self.model
        qvals = target_nn["output"].eval(feed_dict={target_nn["x"]: curr_states})
        theoretical_next_actions = None
        if DOUBLE_DQN:
            theoretical_next_actions = [np.argmax(x) for x in main_nn["output"].eval(feed_dict={main_nn["x"]: curr_states})]

        # Calculate the reward for each experience in the batch
        ybatch = []
        for i in range(len(experience_batch)):
            # If the state is terminal, give the bot the reward for the state
            if experience_batch[i].is_terminal:
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
        feed_dict = {
            main_nn["x"] : prev_states,
            main_nn["action"] : prev_actions,
            main_nn["actual_q_value"] : ybatch
        }
        try:
            self.session.run(main_nn["train"], feed_dict=feed_dict)
        except:
            print("SHIT BROKE")


    def convert_to_network_input(self, state):
        return self.game_props.convert_state_to_network_input(state)

    def refresh_predictor(self):
        copy_ops = NNUtils.cope_source_into_target(MAIN_NETWORK, MAIN_NETWORK)
        self.session.run(copy_ops)

    # Returns an action. Based on the 3rd arg, the action is either random, or taken from the learned policy
    def get_action(self, game_data, is_training=True, is_for_self_play=False):
        # Get a random action if we're training, and the random_action_probability calls for it
        if is_training and random.random() <= self.random_action_probability:
            return NNUtils.get_random_action(self.game_props.network_output_length)
        else:
            # Otherwise, get an action from the policy
            model_to_use = self.self_play_model if is_for_self_play else self.model
            network_input = self.game_props.convert_state_to_network_input(game_data.get_current_state(), reverse=is_for_self_play)
            q_vals_per_action = model_to_use["output"].eval(feed_dict={model_to_use["x"]: [network_input]})[0]
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
        print(datetime.datetime.now())
        print("Num Training Iterations: "+str(self.number_training_iterations))
        print("RANDOM PROB: "+str(self.random_action_probability))

    def debug_screenshot(self):
        a = 3
        #arr = self.convert_to_network_input(experience_batch[0].curr_state)
        #sss = arr.shape
        #grayscaled = self.session.run(self.model["grayscaled"], feed_dict={ self.model["x"]: [arr]})
        #a = grayscaled[0]
        #w, h, c = a.shape
        #b = a.reshape(w, h, c)
        #Image.fromarray(b.astype('uint8')).save(str(self.number_training_iterations)+".png")