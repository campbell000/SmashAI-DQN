# This class is responsible for the majority of our implementation of the DQN algorithm

import numpy as np
import tensorflow as tf
from collections import deque
import random
from reward import Rewarder
from evaluator import Evaluator
from nn import NeuralNetwork
import nn as NN
import os
import uuid

# NOTE: States pushed from the client are in order from least to most recent. Ex: the damages over 4 frames looks like this,
# if the player were to get damaged by 10 every frame
#[s1:10, s2:20, s3:30, s4:40]

# Number of frames the client is sending
NUM_FRAMES_PER_STATE = 2
CURRENT_FRAME_IDX = NUM_FRAMES_PER_STATE

# The frequency at which the client asks for a response (i.e. if 1, then the client sends a request to the server every frame).
SAMPLE_RATE = 2

LEARNING_RATE = 0.00001
NUM_HIDDEN_UNITS = 256
NUM_HIDDEN_UNITS_2 = 128
NUM_HIDDEN_LAYERS = 2
NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
INPUT_LENGTH = (NUM_FRAMES_PER_STATE * (NUM_POSSIBLE_STATES + 13) * 2) # taken from number of non-state params in client data, multiplied by 2 players
OUTPUT_LENGTH = 54 # taken from actions taken from gameConstants.lua
EXPERIENCE_BUFFER_SIZE = 50000
FUTURE_REWARD_DISCOUNT = 0.95  # decay rate of past observations
OBSERVATION_STEPS = 1000  # time steps to observe before training
EXPLORE_STEPS = 500000  # frames over which to anneal epsilon
INITIAL_RANDOM_ACTION_PROB = 1.0  # starting chance of an action being random
FINAL_RANDOM_ACTION_PROB = 0.01  # final chance of an action being random
MINI_BATCH_SIZE = 32  # size of mini batches
NUM_STEPS_FOR_TARGET_NETWORK = 2000
STATUS_REPORT_INTERVAL = 2000
SAVED_ITERATIONS = 100000
DO_EPSILON_DECAY = False
EPSILON = 0.02

PREVIOUS_INDEX = 0
CURRENT_INDEX = 1
ACTION_FROM_PREVIOUS_INDEX = 2


MAIN_NETWORK = "main"
TRAIN_NETWORK = "TRAIN"

class SSB_DQN:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """
    def __init__(self, session, verbose=False):
        self.rewarder = Rewarder(NUM_FRAMES_PER_STATE, SAMPLE_RATE)
        self.experiences = deque()
        self.prev_state = None
        self.action_taken_from_prev_state = None
        self.current_random_action_prob = INITIAL_RANDOM_ACTION_PROB
        self.verbose = verbose
        self.evaluator = Evaluator(self.rewarder)
        self.print_once_map = {}
        self.num_iterations = 0
        self.model = NeuralNetwork(MAIN_NETWORK, session, INPUT_LENGTH, OUTPUT_LENGTH, NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS_2, LEARNING_RATE).build_model()
        self.target_model = NeuralNetwork(TRAIN_NETWORK, session, INPUT_LENGTH, OUTPUT_LENGTH, NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS_2, LEARNING_RATE).build_model()
        self.sess = session
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.saved_network_id = str(uuid.uuid4())
        #self.saver = tf.train.import_meta_graph("./ac48aea8-8f33-4054-a700-3a23a331eda7-1000000.meta")
        #self.saver.restore(self.sess, tf.train.latest_checkpoint("./12-10-911/"))
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    # Given a state, gets an action. Optionally, it also trains the Q-network
    def get_prediction(self, current_state, do_train):
        self.num_iterations += 1
        self.print_once("started", "Got connection, started training")

        # if we have no previous states, then generate a random action and add it to our replay database.
        action = None
        if self.prev_state == None:
            r = random.randint(0,(OUTPUT_LENGTH - 1))
            action = [0] * OUTPUT_LENGTH # Convert to list just to stay consistent
            action[r] = 1
            self.log("First state ever, picking random action")
        else:
            action = self.do_dqn_iteration(current_state, do_train)

            reward_for_current_exp = self.rewarder.calculate_reward([self.prev_state, current_state], self.verbose)
            self.evaluator.add_avg_reward(reward_for_current_exp)

        # Adjust the chance of choosing a random action
        self.adjust_random_probability()

        # Print Status Report
        if self.num_iterations % STATUS_REPORT_INTERVAL == 0:
            self.status_report()

        # Save the network every N iterations
        if self.num_iterations % SAVED_ITERATIONS == 0:
            self.save_network()

        # Regardless of what we've done, update our previous state (and the action we took).
        self.prev_state = current_state
        self.action_taken_from_prev_state = action
        return action

    # This method performs one iteration of the DQN algorithm. It returns an action to perform by the client
    def do_dqn_iteration(self, current_state, do_train):

        # Add the experience to the replay database
        new_experience = [self.prev_state, current_state, self.action_taken_from_prev_state]
        self.add_experience(new_experience)

        # Only train when we are done making our initial observations
        if len(self.experiences) > OBSERVATION_STEPS and do_train:
            self.print_once("started_training", "Training now because we have "+str(len(self.experiences))+" experiences")
            self.train()
        else:
            self.log("Still not training...only gathering data at "+str(len(self.experiences)))

        # get the next action based on a batch of samples in our replay DB
        return self.choose_next_action(current_state)

    # Adds an experience to the Experience DB. Experiences consist of two elements. The first element is previous data,
    # the second is current data
    def add_experience(self, experience):
        self.experiences.append(experience)
        if len(self.experiences) >= EXPERIENCE_BUFFER_SIZE:
            self.experiences.popleft()

    # This method returns an action to execute for the current state. It will either pick a random action, or an action
    # based on the output of the NN.
    def choose_next_action(self, current_state):
        m = self.model
        self.log("Choosing action based on current random probability: "+str(self.current_random_action_prob))

        # Based on self.current_random_action_prob, choose a random action OR chose an action based on the NN.
        if random.random() <= self.current_random_action_prob:
            self.log("Chose randomly")
            r = random.randint(0,(OUTPUT_LENGTH - 1))
            action = [0] * OUTPUT_LENGTH # Convert to list just to stay consistent
            action[r] = 1
            return action
        else:
            # choose an action given our current state, using the output of the NN
            self.log("Chose NOT randomly")
            final_action = [0] * OUTPUT_LENGTH
            tf_current_state = self.convert_client_data_to_tensorflow(current_state)
            output = m["output"].eval(feed_dict={m["x"]: [tf_current_state]})[0]

            # Convert the output into a one hot. The one hot index should be the index with the highest output
            action_index = np.argmax(output)
            final_action[action_index] = 1

            self.evaluator.add_q_value(np.mean(output))

            return final_action

    # This method retrieves a sample batch of experiences from the experience replay DB
    def get_sample_batch(self):
        num_samples = MINI_BATCH_SIZE
        num_total_experiences = len(self.experiences)
        if num_total_experiences < MINI_BATCH_SIZE:
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)

    # This function trains the NN that produces Q-values for every state/action pair.
    def train(self):
        m = self.model
        t = self.target_model

        # Get a mini_batch from the experience replay buffer per DQN
        mini_batch = self.get_sample_batch()

        # Get the necessary data to do DQN
        previous_states = [self.convert_client_data_to_tensorflow(x[PREVIOUS_INDEX]) for x in mini_batch]
        previous_actions = [x[ACTION_FROM_PREVIOUS_INDEX] for x in mini_batch]
        rewards = [self.rewarder.calculate_reward(x) for x in mini_batch]
        current_states = [self.convert_client_data_to_tensorflow(x[CURRENT_INDEX]) for x in mini_batch]
        agents_expected_reward = []

        # Get the expected reward per action from the TARGET Q-Network
        agents_reward_per_action = t["output"].eval(feed_dict={t["x"]: current_states})
        for i in range(len(mini_batch)):
            curr_experience = mini_batch[i]

            # If the state is terminal (which means, if the bot died on the current frame), collect the reward
            if self.rewarder.is_terminal(curr_experience):
                agents_expected_reward.append(rewards[i])
            else:
                exp_reward = rewards[i] + (FUTURE_REWARD_DISCOUNT * np.max(agents_reward_per_action[i]))
                agents_expected_reward.append(exp_reward)

        # Learn that the actions in these states lead to the rewards
        m["sess"].run(m["train"], feed_dict={
            m["x"] : previous_states,
            m["action"] : previous_actions,
            m["target"] : agents_expected_reward
        })

        loss = m["sess"].run(m["loss"], feed_dict={
            m["x"] : previous_states,
            m["action"] : previous_actions,
            m["target"] : agents_expected_reward
        })
        self.evaluator.add_loss(loss)

        # Every N iterations, update the training network with the model of the "real" network
        if self.num_iterations % NUM_STEPS_FOR_TARGET_NETWORK == 0:
            copy_ops = NN.get_copy_var_ops(TRAIN_NETWORK, MAIN_NETWORK)
            self.sess.run(copy_ops)

    # This method converts the data from the client into data for tensorflow.
    def convert_client_data_to_tensorflow(self, data):
        return NN.transform_client_data_for_tensorflow(data, NUM_POSSIBLE_STATES, verbose=self.verbose)

    # Prints a status report to the screen
    def status_report(self):
        print("STATUS REPORT!")
        print("Random Prob: "+str(self.current_random_action_prob))
        print("NUM ITERATIONS: "+str(self.num_iterations))

    # Saves the network (tensorflow variables)
    def save_network(self):
        path = self.current_dir + "/" + self.saved_network_id
        self.saver.save(self.sess, path, global_step=self.num_iterations)

    # This method adjusts the random probability of picking an action to anneal over time.
    def adjust_random_probability(self):
        if DO_EPSILON_DECAY:
            if self.current_random_action_prob > FINAL_RANDOM_ACTION_PROB and len(self.experiences) > OBSERVATION_STEPS:
                self.current_random_action_prob -= (INITIAL_RANDOM_ACTION_PROB - FINAL_RANDOM_ACTION_PROB) / EXPLORE_STEPS
        else:
            self.current_random_action_prob = EPSILON

    # Set to true for more output while the training is ocurring.
    def set_verbose(self, v):
        self.verbose = v

    def log(self, s):
        if self.verbose:
            print(s)

    # Prints output to the screen one time
    def print_once(self, key, msg):
        if key not in self.print_once_map:
            self.print_once_map[key] = 0
            print(msg)