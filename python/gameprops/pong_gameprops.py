from gameprops.gameprops import *
from shared_constants import Constants

# A subclass of the GameProps specific to Super Smash Brothers for the Nintendo 64 Entertainment System (tm) (c).
# We need to know the number of possible states (which varies depending on character), as well
class PongGameProps(GameProps):

    def __init__(self, gameType, network_input_len, network_output_len):
        super(PongGameProps, self).__init__(gameType, network_input_len, network_output_len)

    def get_num_possible_states(self):
        return self.num_possible_states

    def convert_state_to_network_input(self, state):
        return 0