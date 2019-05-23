from abc import ABC

class AbstractRewarder(ABC):

    def __init__(self):
        print("HI")

    def experience_is_terminal(self, experience):
        pass

    def calculate_reward(self, experience):
        pass