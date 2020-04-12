import multiprocessing
import ml_algorithms
import queue
from ml_algorithms.dqn import *
# Models
SARSA_MODEL = 0
DQN_MODEL = 1

class MachineLearningModel(multiprocessing.Process):
    def __init__(self, pipe, use_saved_model, gameprops, rewarder, algorithm, is_self_play, model_to_load, checkpoint_dir_to_load,
                 do_saving):
        super(MachineLearningModel, self).__init__()
        self.pipe = pipe
        self.use_saved_model = use_saved_model
        self.gameprops = gameprops
        self.rewarder = rewarder
        self.model_to_load = model_to_load
        self.algorithm_selection = algorithm
        self.checkpoint_dir_to_load = checkpoint_dir_to_load
        self.is_self_play = is_self_play
        self.saver = None
        self.sample_queue = multiprocessing.Queue(maxsize=100)
        self.session = None
        self.default_graph = None
        self.dropped = 0
        self.algorithm = None
        self.do_saving = do_saving

    def get_action(self, game_data, is_training=True, is_for_self_play=False):
        return self.algorithm.get_action(game_data, is_training, is_for_self_play)

    def train_model(self, training_sample):
        experience = training_sample[-1]
        if not self.sample_queue.full():
            self.sample_queue.put_nowait(training_sample)
        elif self.rewarder.experience_is_terminal(experience):
            self.sample_queue.put(training_sample)
        else:
            self.dropped = self.dropped + 1
            if self.dropped % 1000 == 0:
                print("Dropped 1000 experience because sample queue is full. Dropped: "+str(self.dropped))

    # Returns the current learning algorithm (i.e. DQN, SARSA, etc)
    def get_learning_algorithm(self, pipe, algorithm, sess, gameprops, rewarder):
        if algorithm == DQN_MODEL:
            return DQN(pipe, sess, gameprops, rewarder, False, is_self_play=self.is_self_play)

    # While running, simply loop forever over the training sample queue. As samples come in
    # use them for training
    def run(self):
        print("Starting Child Training Process")
        self.configure_model()
        with self.session.as_default():
            with self.default_graph.as_default():
                while True:
                    training_sample = self.sample_queue.get()
                    self.algorithm.train_model(training_sample)

    def refresh_predictor(self, model_trainer):
        with self.session.as_default():
            with self.default_graph.as_default():
                # Get values of tensors for main predictor network for the model trainer, and copy them into the predictor's
                # main network


                self.algorithm.refresh_predictor()

    def configure_model(self):
        import tensorflow as tf
        # do initial tensorflow configuration
        config = tf.ConfigProto()
        config.gpu_options.allow_growth=True # needed so that TF doesn't freak out when the GPU is actually being used by user/desktop stuff

        # If we're using not using a pre-saved model, initialize the weights to use random scaling
        if not self.use_saved_model:
            print("Initializing random weights")
            tf.variance_scaling_initializer(scale=2)
        else:
            print("Skipping weight init due to saved model being used")

        # Create a tensorflow session and do everything from here on our under that session
        sess = tf.Session(config=config)
        self.session = sess
        self.default_graph = tf.get_default_graph()
        self.algorithm = self.get_learning_algorithm(self.pipe, self.algorithm_selection, sess, self.gameprops, self.rewarder)
        self.gameprops.dump()
        with sess.as_default():
            varsToRestore = tf.contrib.slim.get_variables_to_restore()
            variables_to_restore = [v for v in varsToRestore if v.name.split('/')[0]=='main_network']
            self.saver = tf.train.Saver(variables_to_restore, max_to_keep=1)

        if self.use_saved_model:
            print("**** USING SAVED MODEL: "+self.model_to_load+" *******")
            saver = tf.train.import_meta_graph(self.model_to_load+".meta")
            saver.restore(sess,tf.train.latest_checkpoint(self.checkpoint_dir_to_load))
            print("**** DONE LOADING! ******")
        else:
            # Build the NN models (idiot)
            self.session.run(tf.global_variables_initializer())

        if self.is_self_play:
            print("Initializing self play network with main networks")
            algorithm.init_self_play_networks()
            print("Done init self play network")

