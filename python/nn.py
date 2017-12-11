import numpy as np
import tensorflow as tf
from collections import deque
import random
import ast

# This class is responsible for building a Neural Network used to produce Q-Values
class NeuralNetwork:

    def __init__(self, name, session, input_length, output_length, num_hidden_units, learning_rate):
        self.INPUT_LENGTH = input_length
        self.OUTPUT_LENGTH = output_length
        self.NUM_HIDDEN_UNITS = num_hidden_units
        self.LEARNING_RATE = learning_rate
        self.name = name
        self.session = session

    # This method builds and returns the model for estimating Q values
    def build_model(self):
        with tf.variable_scope(self.name):
            x = tf.placeholder(tf.float32,shape=[None, self.INPUT_LENGTH])
            action = tf.placeholder(tf.float32, [None, self.OUTPUT_LENGTH])
            target = tf.placeholder(tf.float32, [None])

            def weight_var(shape):
                initial = tf.truncated_normal(shape, stddev=0.01)
                return tf.Variable(initial)

            def bias_var(shape):
                initial = tf.constant(0.01, shape=shape)
                return tf.Variable(initial)

            # Create the first hidden layer
            W1 = weight_var([self.INPUT_LENGTH, self.NUM_HIDDEN_UNITS])
            b1 = bias_var([self.NUM_HIDDEN_UNITS])
            layer_1 = tf.nn.relu(tf.add(tf.matmul(x, W1), b1))

            # Create the second hidden layer
            W2 = weight_var([self.NUM_HIDDEN_UNITS, self.NUM_HIDDEN_UNITS])
            b2 = bias_var([self.NUM_HIDDEN_UNITS])
            layer_2 = tf.nn.relu(tf.add(tf.matmul(layer_1, W2), b2))

            # Create the second hidden layer
            W3 = weight_var([self.NUM_HIDDEN_UNITS, self.OUTPUT_LENGTH])
            b3 = bias_var([self.OUTPUT_LENGTH])
            out = tf.add(tf.matmul(layer_2, W3), b3)

            # loss/training steps
            readout_action = tf.reduce_sum(tf.multiply(out, action), reduction_indices=1)
            loss = tf.reduce_mean(tf.square(target- readout_action))
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