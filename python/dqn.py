import numpy as np
import tensorflow as tf
#basic matlab-style plotting
import matplotlib.pyplot as plt

LEARNING_RATE = 0.001
GAMMA = 0.9
EPSILON = 0.1
NUM_HIDDEN_UNITS = 256
NUM_HIDDEN_LAYERS = 2
NUM_POSSIBLE_STATES = 237 # based on highest value in RAM for pikachu
INPUT_LENGTH = NUM_POSSIBLE_STATES + 10 # taken from number of non-state params in client data
OUTPUT_LENGTH = 21 #taken from num buttons/stick inputs

class SSB_DQN:
    def __init__(self):
        self.model = self.build_model()

    # Converts ssb state data into data appropriate for tensorflow
    def transform_client_data(self, data):
        def get_val(client_data, name, player):
            key = str(player)+""+str(name)
            return client_data[key]

        def convert_state_to_vector(client_data, player):
            k = str(player)+"state"
            val = client_data[k]
            return np.eye(NUM_POSSIBLE_STATES)[val]

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

            # Convert the categorical state variable into binary data
            tf_data = tf_data + convert_state_to_vector(data, 1)

    # This method builds and returns the model for estimating Q values
    def build_model(self):
        x = tf.placeholder(tf.float32,shape=[None, INPUT_LENGTH])
        y = tf.placeholder(tf.float32,shape=[None, OUTPUT_LENGTH])

        def weight_var(shape):
            initial = tf.truncated_normal(shape, stddev=0.1)
            return tf.Variable(initial)

        def bias_var(shape):
            initial = tf.constant(0.1, shape=shape)
            return tf.Variable(initial)

        # Create the first hidden layer
        W1 = weight_var([INPUT_LENGTH, NUM_HIDDEN_UNITS])
        b1 = bias_var([NUM_HIDDEN_UNITS])
        layer_1 = tf.add(tf.matmul(x, W1), b1)
        layer_1 = tf.nn.relu(layer_1)

        # Create the second hidden layer
        W2 = weight_var([NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS])
        b2 = bias_var([NUM_HIDDEN_UNITS])
        layer_2 = tf.add(tf.matmul(layer_1, W2), b2)
        layer_2 = tf.nn.relu(layer_2)

        # Create the second hidden layer
        W3 = weight_var([NUM_HIDDEN_UNITS, NUM_HIDDEN_UNITS])
        b3 = bias_var([NUM_HIDDEN_UNITS])
        out = tf.add(tf.matmul(layer_2, W3), b3)

        # Define loss and accuracy for training
        loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=out, labels=y))
        train = tf.train.RMSPropOptimizer(learning_rate=LEARNING_RATE).minimize(loss)

        sess = tf.InteractiveSession()

        return {
            "x" : x,
            "y" : y,
            "output" : out,
            "loss" : loss,
            "train" : train
        }


