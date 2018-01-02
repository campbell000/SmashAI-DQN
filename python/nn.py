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
            layer_1 = tf.nn.relu(tf.add(tf.matmul(x, W1), b1))

            # Create the second hidden layer
            W2 = weight_var([self.NUM_HIDDEN_UNITS, self.NUM_HIDDEN_UNITS_SECOND_LAYER])
            b2 = bias_var([self.NUM_HIDDEN_UNITS_SECOND_LAYER])
            layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, W2), b2))

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

# Converts ssb state data into data appropriate for tensorflow. If there's more than one
def transform_client_data_for_tensorflow(data, num_possible_states, num_frames_per_state):

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
        v = [0] * num_possible_states
        try:
            v[val] = 1
        except:
            print(val)
            print(v)
            raise Exception("State value exceeded expected maximum number of states!")

        return v

    # DO NOT MESS WITH THIS ORDER! THIS IS THE ORDER THAT THE INPUTS WILL GET FED INTO TENSORFLOW!
    tf_data = []
    for frame in range(1, num_frames_per_state+1): # Lua is 1-indexed.....ugh
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