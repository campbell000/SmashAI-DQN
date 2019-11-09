import numpy as np
import tensorflow as tf
from collections import deque
from tensorflow.losses import huber_loss
import random
import ast

# This class is responsible for building a Neural Network used to produce Q-Values
class NeuralNetwork:

    def __init__(self, name, session, input_length, output_length, nodes_per_layer_arr, learning_rate, is_training=True,
                 huber_loss=False, include_dropout=False, dropout_rate=0.05):
        self.input_length = input_length
        self.output_length = output_length
        self.learning_rate = learning_rate
        self.name = name
        self.session = session
        self.is_training = is_training
        self.dropout_rate = dropout_rate
        self.map = None
        self.nodes_per_layer_arr = nodes_per_layer_arr
        self.include_dropout = include_dropout
        self.is_huber_loss = huber_loss
    def get_map(self):
        return self.map


    def predict(self, state):
        return self.map["output"].eval(feed_dict={self.map["x"]: state})

    # This method builds and returns the model for estimating Q values
    def build(self):
        with tf.variable_scope(self.name):
            x = tf.placeholder(tf.float32, [None, self.input_length]) # rows of input vectors
            actions = tf.placeholder(tf.float32, [None, self.output_length]) # should be rows of [0,0,...1,0,0]
            rewards = tf.placeholder(tf.float32, [None]) # should be rows of one value
            layers = []

            # Create X numbers of layers
            prev_drop_layer = None
            for layer in range(len(self.nodes_per_layer_arr)):
                num_nodes = self.nodes_per_layer_arr[layer]

                # If first layer, use the NN's input
                if prev_drop_layer is None:
                    hidden_layer = tf.layers.dense(x, num_nodes, activation=tf.nn.relu)
                else:
                    hidden_layer = tf.layers.dense(prev_drop_layer, num_nodes, activation=tf.nn.relu)

                layers.append(["layer "+str(layer), hidden_layer])
                if self.include_dropout:
                    hidden_dropout = tf.layers.dropout(hidden_layer, rate=self.dropout_rate, training=self.is_training)
                    prev_drop_layer = hidden_dropout
                    layers.append(["dropout "+str(layer), hidden_dropout])
                else:
                    prev_drop_layer = hidden_layer

            # Use the last dropout layer to create the final output layer
            output_layer = tf.layers.dense(prev_drop_layer, self.output_length)
            layers.append(["final output layer", output_layer])

            # Do huber loss if specified. Otherwise do MSE
            if self.is_huber_loss:
                q_action = tf.reduce_sum(tf.multiply(output_layer, actions), reduction_indices=1)
                loss = huber_loss(rewards, q_action)
            else:
                q_action = tf.reduce_sum(tf.multiply(output_layer, actions), reduction_indices=1)
                loss = tf.reduce_mean(tf.square(rewards - q_action))

            # Set up training operation
            train = tf.train.AdamOptimizer(self.learning_rate).minimize(loss)

            self.map = {
                "layers" : layers,
                "c" : [self.input_length, self.output_length],
                "x" : x,
                "actual_q_value" : rewards,
                "output" : output_layer,
                "loss" : loss,
                "train" : train,
                "action" : actions
            }
            return self.map
