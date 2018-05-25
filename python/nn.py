import numpy as np
import tensorflow as tf
from collections import deque
import random
import ast

# This class is responsible for building a Neural Network used to produce Q-Values
class NeuralNetwork:

    def __init__(self, name, session, input_length, output_length,learning_rate, is_training=True, dropout_rate=0.05):
        self.input_length = input_length
        self.output_length = output_length
        self.learning_rate = learning_rate
        self.name = name
        self.session = session
        self.is_training = is_training
        self.dropout_rate = dropout_rate

    # This method builds and returns the model for estimating Q values
    def build_model(self, num_layers, nodes_per_layer):
        with tf.variable_scope(self.name):
            x = tf.placeholder(tf.float32, [None, self.input_length]) # rows of input vectors
            selected_action = tf.placeholder(tf.float32, [None, self.output_length]) # should be rows of [0,0,...1,0,0]
            actual_q_values_for_action_taken = tf.placeholder(tf.float32, [None]) # should be rows of one value

            # Create X numbers of layers
            prev_drop_layer = None
            hidden_layer = None
            hidden_dropout = None
            for layer in range(num_layers):
                num_nodes = nodes_per_layer[layer]
                # If first layer, use the NN's input
                if prev_drop_layer is None:
                    hidden_layer = tf.layers.dense(x, num_nodes, activation=tf.nn.relu)
                else:
                    hidden_layer = tf.layers.dense(prev_drop_layer, num_nodes, activation=tf.nn.relu)

                hidden_dropout = tf.layers.dropout(hidden_layer, rate=self.dropout_rate, training=self.is_training)
                prev_drop_layer = hidden_dropout

            # Use the last dropout layer to create the final output layer
            output_layer = tf.layers.dense(prev_drop_layer)

            # Get loss between predicted and actual Q-values for the SELECTED ACTION ONLY
            # This works by multiplying each row (each row is one prediction in the batch) with the index of the selected action
            predicted_q_value_for_taken_action = tf.reduce_sum(tf.multiply(output_layer, selected_action), axis=1)
            loss = tf.reduce_mean(tf.square(actual_q_values_for_action_taken - predicted_q_value_for_taken_action))

            # Set up training operation
            train = tf.train.AdamOptimizer(self.learning_rate).minimize(loss)

            return {
                "x" : x,
                "predicted_q_value" : predicted_q_value_for_taken_action,
                "actual_q_value" : actual_q_values_for_action_taken,
                "output" : output_layer,
                "loss" : loss,
                "train" : train,
                "sess" : self.session
            }

