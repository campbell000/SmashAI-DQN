
from abc import ABC
class LearningModel(ABC):

    # Initialize defaults for all of the variables
    def __init__(self, session, game_props, rewarder):
        self.session = session
        self.game_props = game_props
        self.rewarder = rewarder

    # Returns the length of a client's history that we need to train. I.e. DQN simply needs one experience, while n-step
    # SARSA needs n experiences
    def get_client_experience_memory_size(self):
        pass

    # Given a game state, returns the best action to perform
    def get_action(self, game_data):
        pass

    # Trains the model one iteration (i.e. usually one mini batch)
    def train_model(self, training_sample):
        pass