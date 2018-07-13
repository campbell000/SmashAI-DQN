from abc import ABC

class AbstractRewarder(ABC):

    def __init__(self, num_frames_per_state):
        self.num_frames_per_state = num_frames_per_state

    def experience_is_terminal(self, experience):
        pass

    def calculate_reward(self, experience):
        pass