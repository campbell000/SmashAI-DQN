import numpy as np
import tensorflow as tf
import random
import os
import uuid

class NeuralNetworkUtils:
    # This method returns operations to copy the weights/variables from the src network to the destination network.
    @staticmethod
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
    @staticmethod
    def transform_client_data_for_tensorflow(state, num_possible_states):

        # Iterate through each state's frames, and then through each player's data
        tf_data = []
        for frame in sorted(state.get_frames()):
            for player_data in sorted(frame.get_players()):
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
                tf_data = tf_data + NeuralNetworkUtils.convert_state_to_vector(player_data["state"], num_possible_states)
        return tf_data

    # This method converts the state of the player into a one-hot vector. Required since
    # the state doesn't really mean anything in a numerical sense.
    @staticmethod
    def convert_state_to_vector(state_value, num_possible_states):
        v = [0] * num_possible_states
        try:
            v[state_value] = 1
        except:
            print(state_value)
            print(v)
            raise Exception("State value exceeded expected maximum number of states!")

        return v

    @staticmethod
    def get_one_hot(value, num_states):
        return np.eye(num_states)[value]