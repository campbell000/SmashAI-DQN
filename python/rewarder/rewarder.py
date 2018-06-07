from abc import ABC

class AbstractRewarder(ABC):

    def experience_is_terminal(self, experience):
        pass

    def calculate_reward(self, experience):
        pass