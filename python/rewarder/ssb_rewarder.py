from rewarder.rewarder import *

class SSBRewarder(AbstractRewarder):

    def experience_is_terminal(self, experience):
        return True

    def calculate_reward(self, experience):
        return 0