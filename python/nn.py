import numpy as np
import tensorflow as tf
from collections import deque
import random
import ast

# This class is responsible for building a Neural Network used to produce Q-Values
class NeuralNetwork:

    def __init__(self, name, session, input_length, output_length, num_hidden_units, num_hidden_units_2, learning_rate):
        self.INPUT_LENGTH = input_length
        self.OUTPUT_LENGTH = output_length
        self.NUM_HIDDEN_UNITS = num_hidden_units
        self.NUM_HIDDEN_UNITS_SECOND_LAYER = num_hidden_units_2
        self.LEARNING_RATE = learning_rate
        self.name = name
        self.session = session

    def leaky_softplus(self, x, alpha=0.01):
        "Really just a special case of log_sum_exp."
        ax = alpha * x
        maxes = tf.stop_gradient(tf.maximum(ax, x))
        return maxes + tf.log(tf.exp(ax - maxes) + tf.exp(x - maxes))

    # This method builds and returns the model for estimating Q values
    def build_model(self):

        def weight_var(shape):
            initial = tf.truncated_normal(shape, stddev=0.01)
            return tf.Variable(initial)

        def bias_var(shape):
            initial = tf.constant(0.01, shape=shape)
            return tf.Variable(initial)

        with tf.variable_scope(self.name):
            x = tf.placeholder(tf.float32, [None, self.INPUT_LENGTH])
            action = tf.placeholder(tf.float32, [None, self.OUTPUT_LENGTH])
            target = tf.placeholder(tf.float32, [None])

            # Create the first hidden layer
            W1 = weight_var([self.INPUT_LENGTH, self.NUM_HIDDEN_UNITS])
            b1 = bias_var([self.NUM_HIDDEN_UNITS])
            layer_1 = self.leaky_softplus(tf.add(tf.matmul(x, W1), b1))

            # Create the second hidden layer
            W2 = weight_var([self.NUM_HIDDEN_UNITS, self.NUM_HIDDEN_UNITS_SECOND_LAYER])
            b2 = bias_var([self.NUM_HIDDEN_UNITS_SECOND_LAYER])
            layer_2 = self.leaky_softplus(tf.add(tf.matmul(layer_1, W2), b2))

            # Create the output layer
            W3 = weight_var([self.NUM_HIDDEN_UNITS_SECOND_LAYER, self.OUTPUT_LENGTH])
            b3 = bias_var([self.OUTPUT_LENGTH])
            out = tf.add(tf.matmul(layer_2, W3), b3)

            # loss/training steps
            readout_action = tf.reduce_sum(tf.multiply(out, action), axis=1)
            loss = tf.reduce_mean(tf.square(target - readout_action))
            train = tf.train.AdamOptimizer(self.LEARNING_RATE).minimize(loss)

            return {
                "x" : x,
                "action" : action,
                "readout_action" : readout_action,
                "target" : target,
                "output" : out,
                "loss" : loss,
                "train" : train,
                "sess" : self.session
            }

# This method returns operations to copy the weights/variables from the src network to the destination network.
def get_copy_var_ops(dest_name, src_name):
    op_holder = []

    src_vars = tf.get_collection(
        tf.GraphKeys.TRAINABLE_VARIABLES, scope=src_name)
    dest_vars = tf.get_collection(
        tf.GraphKeys.TRAINABLE_VARIABLES, scope=dest_name)

    for src_var, dest_var in zip(src_vars, dest_vars):
        op_holder.append(dest_var.assign(src_var.value()))

    return op_holder

# This method converts the state of the player into a one-hot vector. Required since
# the state doesn't really mean anything in a numerical sense.
def convert_state_to_vector(state_value, num_possible_states):
    v = [0] * num_possible_states
    try:
        v[state_value] = 1
    except:
        print(state_value)
        print(v)
        raise Exception("State value exceeded expected maximum number of states!")

    return v

# Converts ssb state data into data appropriate for tensorflow. If there's more than one
def transform_client_data_for_tensorflow(data, num_possible_states, verbose=False):

    # Iterate through each state, and each state's player data, and flatten all of it into one vector to feed into TF.
    tf_data = []
    for state in data:
        for player_data in state:
            # Append numeric data to vector. DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
            tf_data.append(player_data["xp"])
            tf_data.append(player_data["xv"])
            tf_data.append(player_data["xa"])
            tf_data.append(player_data["yp"])
            tf_data.append(player_data["yv"])
            tf_data.append(player_data["ya"])
            tf_data.append(player_data["shield_size"])
            tf_data.append(player_data["shield_recovery_time"])
            tf_data.append(player_data["direction"])
            tf_data.append(player_data["jumps_remaining"])
            tf_data.append(player_data["damage"])
            tf_data.append(player_data["state_frame"])
            tf_data.append(player_data["is_in_air"])

            # Convert the categorical state variable into binary data
            tf_data = tf_data + convert_state_to_vector(player_data["state"], num_possible_states)
    return tf_data