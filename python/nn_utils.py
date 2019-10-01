import numpy as np
import tensorflow as tf
import random
import os
import uuid

class NeuralNetworkUtils:
    # This method returns operations to copy the weights/variables from the src network to the destination network.
    @staticmethod
    def cope_source_into_target(src_name, dest_name):
        op_holder = []

        src_vars = tf.get_collection(
            tf.GraphKeys.TRAINABLE_VARIABLES, scope=src_name)
        dest_vars = tf.get_collection(
            tf.GraphKeys.TRAINABLE_VARIABLES, scope=dest_name)

        for src_var, dest_var in zip(src_vars, dest_vars):
            op_holder.append(dest_var.assign(src_var.value()))

        return op_holder

    @staticmethod
    def get_one_hot(value, num_possible_classes):
        return np.eye(num_possible_classes)[value]