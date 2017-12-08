import numpy as np
import tensorflow as tf
from collections import deque
import random
from reward import Rewarder
from evaluator import Evaluator
import ast

LEARNING_RATE = 0.001
GAMMA = 0.9
EPSILON = 0.1
NUM_HIDDEN_UNITS = 512
NUM_HIDDEN_LAYERS = 2
NUM_POSSIBLE_STATES = 254 # based on highest value in RAM for pikachu, which looks like 0xFD
INPUT_LENGTH = (NUM_POSSIBLE_STATES + 11) * 2 # taken from number of non-state params in client data, multiplied by 2 players
OUTPUT_LENGTH = 43 # taken from actions taken from gameConstants.lua
EXPERIENCE_BUFFER_SIZE = 60000
FUTURE_REWARD_DISCOUNT = 0.99  # decay rate of past observations
OBSERVATION_STEPS = 50000  # time steps to observe before training
EXPLORE_STEPS = 500000  # frames over which to anneal epsilon
INITIAL_RANDOM_ACTION_PROB = 1.0  # starting chance of an action being random
FINAL_RANDOM_ACTION_PROB = 0.05  # final chance of an action being random
MINI_BATCH_SIZE = 20  # size of mini batches


class SSB_DQN:
    """
    Inspiration for this file comes from # https://github.com/DanielSlater/PyGamePlayer/blob/master/examples/deep_q_pong_player.py.
    In it, the developer implements a DQN algorithm for PONG using image data (substantially different than my project).
    """

    def __init__(self, verbose=False):
        self.model = self.build_model()
        self.rewarder = Rewarder()
        self.experiences = deque()
        self.prev_state = None
        self.prev_action = None
        self.current_random_action_prob = INITIAL_RANDOM_ACTION_PROB
        self.verbose = verbose
        self.evaluator = Evaluator()
        self.print_once_map = {}
        self.num_iterations = 0

    def set_verbose(self, v):
        self.verbose = v

    def log(self, s):
        if self.verbose:
            print(s)

    def print_once(self, key, msg):
        if key not in self.print_once_map:
            self.print_once_map[key] = 0
            print(msg)

    # experiences consist of two elements. The first element is previous data, the second is current data
    def add_experience(self, experience):
        self.experiences.append(experience)
        if len(self.experiences) >= EXPERIENCE_BUFFER_SIZE:
            self.experiences.popleft()

    # Given a state, gets an action. Optionally, it also trains the Q-network
    def get_prediction(self, current_state, do_train):
        self.num_iterations += 1

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
                self.print_once("a", "Started Training!")
                self.log("Training now because we have "+str(len(self.experiences))+" experiences")
                self.train()
            else:
                self.log("Still not training...only gathering data at "+str(len(self.experiences)))

            # get the next action based on a batch of samples in our replay DB
            action = self.choose_next_action(current_state)

        self.log("Chose action:\n"+str(action))

        if self.num_iterations % 50000 == 0:
            self.status_report()

        # Adjust the change of chosing a random action
        self.adjust_random_probability()

        # Regardles of what we've done, update our previous state and return the action
        self.prev_state = current_state
        self.prev_action = action
        return action

    def status_report(self):
        print("STATUS REPORT!")
        print("Random Prob: "+str(self.current_random_action_prob))
        print("NUM ITERATIONS: "+str(self.num_iterations))


    def adjust_random_probability(self):
        if self.current_random_action_prob > FINAL_RANDOM_ACTION_PROB and len(self.experiences) > OBSERVATION_STEPS:
            self.current_random_action_prob -= (INITIAL_RANDOM_ACTION_PROB - FINAL_RANDOM_ACTION_PROB) / EXPLORE_STEPS

    def choose_next_action(self, current_state):
        # Transform the map of string and categorical data into strictly numerical data
        m = self.model
        self.log("Choosing action based on current random probability: "+str(self.current_random_action_prob))
        if random.random() <= self.current_random_action_prob:
            self.log("Chose randomly")
            r = random.randint(0,(OUTPUT_LENGTH - 1))
            action = [0] * OUTPUT_LENGTH # Convert to list just to stay consistent
            action[r] = 1
            return action
        else:
            self.log("Chose NOT randomly")
            # choose an action given our last state
            final_action = [0] * OUTPUT_LENGTH
            tf_current_state = self.transform_client_data_for_tensorflow(current_state)
            output = m["output"].eval(feed_dict={m["x"]: [tf_current_state]})[0]

            # Convert the output into a one hot. The one hot index should be the index with the highest output
            action_index = np.argmax(output)
            final_action[action_index] = 1

            # Log the max q value for evaluation purposes
            self.evaluator.add_q_value(np.max(output))
            return final_action

    def get_sample_batch(self):
        num_samples = MINI_BATCH_SIZE
        num_total_experiences = len(self.experiences)
        if num_total_experiences < MINI_BATCH_SIZE:
            num_samples = num_total_experiences
        return random.sample(self.experiences, num_samples)

    # Converts ssb state data into data appropriate for tensorflow
    def transform_client_data_for_tensorflow(self, data):
        def get_val(client_data, name, player):
            key = str(player)+""+str(name)
            return client_data[key] # Convert the string into a float or int

        # This method converts the state of the player into a one-hot vector. Required since
        # the state doesn't really mean anything in a numerical sense.
        def convert_state_to_vector(client_data, player):
            k = str(player)+"state"
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
        for i in range(1, 3):
            # Append numeric data to vector
            tf_data.append(get_val(data, "xp", i))
            tf_data.append(get_val(data, "xv", i))
            tf_data.append(get_val(data, "xa", i))
            tf_data.append(get_val(data, "yp", i))
            tf_data.append(get_val(data, "yv", i))
            tf_data.append(get_val(data, "ya", i))
            tf_data.append(get_val(data, "shield_size", i))
            tf_data.append(get_val(data, "shield_recovery_time", i))
            tf_data.append(get_val(data, "direction", i))
            tf_data.append(get_val(data, "jumps_remaining", i))
            tf_data.append(get_val(data, "damage", i))

            # Convert the categorical state variable into binary data
            tf_data = tf_data + convert_state_to_vector(data, i)
        return tf_data

    # This method builds and returns the model for estimating Q values
    def build_model(self):
        x = tf.placeholder(tf.float32,shape=[None, INPUT_LENGTH])
        action = tf.placeholder(tf.float32, [None, OUTPUT_LENGTH])
        target = tf.placeholder(tf.float32, [None])

        def weight_var(shape):
            initial = tf.truncated_normal(shape, stddev=0.01)
            return tf.Variable(initial)

        def bias_var(shape):
            initial = tf.constant(0.01, shape=shape)
            return tf.Variable(initial)

        # Create the first hidden layer
        W1 = weight_var([INPUT_LENGTH, NUM_HIDDEN_UNITS])
        b1 = bias_var([NUM_HIDDEN_UNITS])
        layer_1 = tf.nn.relu(tf.add(tf.matmul(x, W1), b1))

        # Create the second hidden layer
        W2 = weight_var([NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS])
        b2 = bias_var([NUM_HIDDEN_UNITS])
        layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, W2), b2))

        # Create the second hidden layer
        W3 = weight_var([NUM_HIDDEN_UNITS, OUTPUT_LENGTH])
        b3 = bias_var([OUTPUT_LENGTH])
        out = tf.add(tf.matmul(layer_2, W3), b3)

        # loss/training steps
        loss = tf.nn.softmax_cross_entropy_with_logits(logits=out, labels=action)
        train = tf.train.AdamOptimizer(LEARNING_RATE).minimize(loss)

        sess = tf.InteractiveSession()
        sess.run(tf.initialize_all_variables())

        return {
            "x" : x,
            "action" : action,
            "target" : target,
            "output" : out,
            "loss" : loss,
            "train" : train,
            "sess" : sess
        }

    def train(self):
        m = self.model
        # Get a mini_batch from the experience replay buffer per DQN
        mini_batch = self.get_sample_batch()

        # Get the necessary data to do DQN
        previous_states = [self.transform_client_data_for_tensorflow(x[0]) for x in mini_batch]
        previous_actions = [x[0]["action"] for x in mini_batch]
        rewards = [self.rewarder.calculate_reward(x) for x in mini_batch]
        current_states = [self.transform_client_data_for_tensorflow(x[1]) for x in mini_batch]
        agents_expected_reward = []

        # Get the expected reward per action from the Q-Network
        agents_reward_per_action = m["output"].eval(feed_dict={m["x"]: current_states})
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