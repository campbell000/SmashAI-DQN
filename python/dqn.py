# This class is responsible for the majority of our implementation of the DQN algorithm

import numpy as np
import tensorflow as tf
from collections import deque
import random
from reward import Rewarder
from evaluator import Evaluator
from nn import NeuralNetwork
import os
import uuid

# NOTE: States pushed from the client are in order from least to most recent. Ex: the damages over 4 frames looks like this,
# if the player were to get damaged by 10 every frame
#[s1:10, s2:20, s3:30, s4:40]

# Number of frames the client is sending
NUM_FRAMES_PER_STATE = 4

# The frequency at which the client asks for a response (i.e. if 1, then the client sends a request to the server every frame).
SAMPLE_RATE = 2

LEARNING_RATE = 0.00001
NUM_HIDDEN_UNITS = 512
NUM_HIDDEN_UNITS_2 = 256
NUM_HIDDEN_LAYERS = 2
NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
INPUT_LENGTH = (NUM_FRAMES_PER_STATE * (NUM_POSSIBLE_STATES + 13) * 2) # taken from number of non-state params in client data, multiplied by 2 players
OUTPUT_LENGTH = 54 # taken from actions taken from gameConstants.lua
EXPERIENCE_BUFFER_SIZE = 50000
FUTURE_REWARD_DISCOUNT = 0.95  # decay rate of past observations
OBSERVATION_STEPS = 40000  # time steps to observe before training
EXPLORE_STEPS = 1000000  # frames over which to anneal epsilon
INITIAL_RANDOM_ACTION_PROB = 1.0  # starting chance of an action being random
FINAL_RANDOM_ACTION_PROB = 0.01  # final chance of an action being random
MINI_BATCH_SIZE = 32  # size of mini batches
NUM_STEPS_FOR_TARGET_NETWORK = 2000
STATUS_REPORT_INTERVAL = 10000
ACTION_REPORT_INTERVAL = 500
SAVED_ITERATIONS = 100000
LOSS_ITERVAL = 1000


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
        self.prev_action = None
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

    # Adds an experience to the Experience DB. Experiences consist of two elements. The first element is previous data,
    # the second is current data
    def add_experience(self, experience):
        self.experiences.append(experience)
        if len(self.experiences) >= EXPERIENCE_BUFFER_SIZE:
            self.experiences.popleft()

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
            # Add the new experience to the replay DB
            self.prev_state["action"] = self.prev_action
            new_experience = [self.prev_state, current_state]
            self.add_experience(new_experience)

            # If we're in verbose mode, show the current reward for the current frame. You know, to make sure thing work.
            if self.verbose:
                self.rewarder.calculate_reward(new_experience, for_current_verbose=True)

            # Only train when we are done making our initial observations
            if len(self.experiences) > OBSERVATION_STEPS and do_train:
                self.print_once("started_training", "Training now because we have "+str(len(self.experiences))+" experiences")
                self.train()
            else:
                self.log("Still not training...only gathering data at "+str(len(self.experiences)))

            # get the next action based on a batch of samples in our replay DB
            action = self.choose_next_action(current_state)

            # Record the KO count for the current episode
            self.evaluator.add_kill_reward_state(new_experience)

        self.log("Chose action:\n"+str(action))

        # Print Status Report
        if self.num_iterations % STATUS_REPORT_INTERVAL == 0:
            self.status_report()

        # Print Action chosen, just so we get a better idea of what's happening
        if self.num_iterations % ACTION_REPORT_INTERVAL == 0:
            print("CHosen action: \n"+str(action))

        # Save the network every N iterations
        if self.num_iterations % SAVED_ITERATIONS == 0:
            self.save_network()

        # Adjust the change of chosing a random action
        self.adjust_random_probability()

        # Regardles of what we've done, update our previous state and return the action
        self.prev_state = current_state
        self.prev_action = action
        return action

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
        if self.current_random_action_prob > FINAL_RANDOM_ACTION_PROB and len(self.experiences) > OBSERVATION_STEPS:
            self.current_random_action_prob -= (INITIAL_RANDOM_ACTION_PROB - FINAL_RANDOM_ACTION_PROB) / EXPLORE_STEPS

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
            tf_current_state = self.transform_client_data_for_tensorflow(current_state)
            output = m["output"].eval(feed_dict={m["x"]: [tf_current_state]})[0]

            # Convert the output into a one hot. The one hot index should be the index with the highest output
            self.log("Q-Values for current action:\n"+str(output))
            action_index = np.argmax(output)
            final_action[action_index] = 1

            # Log the max q value for evaluation purposes
            self.evaluator.add_q_value(np.average(output))
            return final_action

    # This method retrieves a sample batch of experiences from the experience replay DB
    def get_sample_batch(self):
        num_samples = MINI_BATCH_SIZE
        num_total_experiences = len(self.experiences)
        if num_total_experiences < MINI_BATCH_SIZE:
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)

    # Converts ssb state data into data appropriate for tensorflow. If there's more than one
    def transform_client_data_for_tensorflow(self, data):

        def get_val(client_data, name, frame, player):
            key = "s"+str(frame)+"_"+str(player)+""+str(name)
            if key not in client_data:
                raise Exception("Looked for "+str(key)+" in the client's data, but we couldn't find it!")
            return client_data[key] # Convert the string into a float or int

        # This method converts the state of the player into a one-hot vector. Required since
        # the state doesn't really mean anything in a numerical sense.
        def convert_state_to_vector(client_data, frame, player):
            k = "s"+str(frame)+"_"+str(player)+"state"
            val = client_data[k]
            v = [0] * NUM_POSSIBLE_STATES
            try:
                v[val] = 1
            except:
                print(val)
                print(v)
                raise Exception("State value exceeded expected macimum number of states!")

            return v

        # DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
        tf_data = []
        for frame in range(1, NUM_FRAMES_PER_STATE+1): # Lua is 1-indexed.....ugh
            for i in range(1, 3):
                # Append numeric data to vector
                tf_data.append(get_val(data, "xp", frame, i))
                tf_data.append(get_val(data, "xv", frame, i))
                tf_data.append(get_val(data, "xa", frame, i))
                tf_data.append(get_val(data, "yp", frame, i))
                tf_data.append(get_val(data, "yv", frame, i))
                tf_data.append(get_val(data, "ya", frame, i))
                tf_data.append(get_val(data, "shield_size", frame, i))
                tf_data.append(get_val(data, "shield_recovery_time", frame, i))
                tf_data.append(get_val(data, "direction", frame, i))
                tf_data.append(get_val(data, "jumps_remaining", frame, i))
                tf_data.append(get_val(data, "damage", frame, i))
                tf_data.append(get_val(data, "state_frame", frame, i))
                tf_data.append(get_val(data, "is_in_air", frame, i))

                # Convert the categorical state variable into binary data
                tf_data = tf_data + convert_state_to_vector(data, frame, i)
        return tf_data

    # This function trains the NN that produces Q-values for every state/action pair.
    def train(self):
        m = self.model
        t = self.target_model

        # Get a mini_batch from the experience replay buffer per DQN
        mini_batch = self.get_sample_batch()

        # Get the necessary data to do DQN
        previous_states = [self.transform_client_data_for_tensorflow(x[0]) for x in mini_batch]
        previous_actions = [x[0]["action"] for x in mini_batch]
        rewards = [self.rewarder.calculate_reward(x) for x in mini_batch]
        current_states = [self.transform_client_data_for_tensorflow(x[1]) for x in mini_batch]
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

        # Every N iterations, update the training network with the model of the "real" network
        if self.num_iterations % NUM_STEPS_FOR_TARGET_NETWORK == 0:
            copy_ops = self.get_copy_var_ops(TRAIN_NETWORK, MAIN_NETWORK)
            self.sess.run(copy_ops)

    def get_copy_var_ops(self, dest_name, src_name):
        """Creates TF operations that copy weights from `src_scope` to `dest_scope`
        Args:
            dest_scope_name (str): Destination weights (copy to)
            src_scope_name (str): Source weight (copy from)
        Returns:
            List[tf.Operation]: Update operations are created and returned
        """
        # Copy variables src_scope to dest_scope
        op_holder = []

        src_vars = tf.get_collection(
            tf.GraphKeys.TRAINABLE_VARIABLES, scope=src_name)
        dest_vars = tf.get_collection(
            tf.GraphKeys.TRAINABLE_VARIABLES, scope=dest_name)

        for src_var, dest_var in zip(src_vars, dest_vars):
            op_holder.append(dest_var.assign(src_var.value()))

        return op_holder