from rewarder.rewarder import *

class SSBRewarder(Rewarder):

    def experience_is_terminal(self, experience):
        return True

    def calculate_reward(self, experience):
        return 0