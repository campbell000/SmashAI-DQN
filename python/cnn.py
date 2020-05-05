import numpy as np
import tensorflow as tf
from collections import deque
from tensorflow.losses import huber_loss
import random
import ast
#import imageio
#from PIL import Image
#import PIL
import uuid

# This class is responsible for building a Neural Network used to produce Q-Values
class ConvolutionalNeuralNetwork:

    def __init__(self, name, input_length, preprocessed_input_length, output_length, nodes_per_fc_layer_arr, cnn_params,
                 learning_rate, batch_size, img_scaling_factor, do_grayscale=True, is_training=True):
        self.input_length = input_length
        self.output_length = output_length
        self.learning_rate = learning_rate
        self.name = name
        self.is_training = is_training
        self.cnn_params = cnn_params
        self.map = None
        self.nodes_per_fc_layer_arr = nodes_per_fc_layer_arr
        self.is_huber_loss = huber_loss
        self.batch_size = batch_size
        self.img_scaling_factor = img_scaling_factor
        self.preprocessed_input_length = preprocessed_input_length
        self.do_grayscale = do_grayscale

    def get_map(self):
        return self.map

    def predict(self, state):
        return self.map["output"].eval(feed_dict={self.map["x"]: state})

    # This method builds and returns the model for estimating Q values
    def build(self):
        with tf.variable_scope(self.name):
            # image preprocessing: convert to grayscale and downsample
            x = tf.placeholder(tf.float32, shape=((None, ) + self.input_length)) # rows of input vectors
            input_shape = x.get_shape().as_list()
            height = int(input_shape[1] / self.img_scaling_factor)
            width = int(input_shape[2] / self.img_scaling_factor)
            downsampled = tf.image.resize_images(x,size=[height, width],
                                                 method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
            grayscaled = tf.image.rgb_to_grayscale(downsampled) if self.do_grayscale else downsampled

            actions = tf.placeholder(tf.float32, [None, self.output_length]) # should be rows of [0,0,...1,0,0]
            rewards = tf.placeholder(tf.float32, [None]) # should be rows of one value
            layers = []

            # expects CNN params to be in format [[num_filters, filter_size, stride]]
            prev_layer = None
            for cnn_param_set in self.cnn_params:
                num_filters = cnn_param_set[0]
                filter_size = cnn_param_set[1]
                stride = cnn_param_set[2]
                if prev_layer is None:
                    prev_layer = tf.layers.conv2d(inputs=grayscaled, filters=num_filters, kernel_size=filter_size, strides=stride, activation=tf.nn.relu)
                else:
                    prev_layer = tf.layers.conv2d(inputs=prev_layer, filters=num_filters, kernel_size=filter_size, strides=stride, activation=tf.nn.relu)

            # Create X numbers of FC layers
            for layer in range(len(self.nodes_per_fc_layer_arr)):
                num_nodes = self.nodes_per_fc_layer_arr[layer]

                # If first layer, use the NN's input
                if prev_layer is None:
                    hidden_layer = tf.layers.dense(x, num_nodes, activation=tf.nn.relu)
                else:
                    hidden_layer = tf.layers.dense(prev_layer, num_nodes, activation=tf.nn.relu)

                layers.append(["layer "+str(layer), hidden_layer])
                prev_layer = hidden_layer

            # Flatten to feed into last FC output layer
            flattened_last_layer = tf.layers.flatten(prev_layer)

            # Use the last dropout layer to create the final output layer
            output_layer = tf.layers.dense(flattened_last_layer, self.output_length)
            layers.append(["final output layer", output_layer])

            q_action = tf.reduce_sum(tf.multiply(output_layer, actions), reduction_indices=1)
            loss = tf.reduce_mean(tf.square(rewards - q_action))

            # Set up training operation
            train = tf.train.AdamOptimizer(self.learning_rate).minimize(loss)

            self.map = {
                "layers" : layers,
                "c" : [self.input_length, self.output_length],
                "x" : x,
                "grayscaled": grayscaled,
                "downsampled": downsampled,
                "actual_q_value" : rewards,
                "output" : output_layer,
                "loss" : loss,
                "train" : train,
                "action" : actions
            }
            return self.map
