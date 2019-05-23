from rewarder.rewarder import *
from gameprops.gameprops import *
from gameprops.pong_gameprops import *
from gamedata_parser import *

class PongRewarder(AbstractRewarder):

    def __init__(self):
        super(AbstractRewarder, self).__init__()

    # the experience is termainl if one player has '10' in the current state (any frame).
    def experience_is_terminal(self, experience):
        reward = self.calculate_reward(experience)
        return reward != 0

    # Take the difference between the max scores for prev/current state. Each state could have multiple frames; we're
    # only concerned with the difference between the maxes of each state's frames
    # NOTE: reward is player 1-centric!
    def calculate_reward(self, experience, verbose=False):

        player1_max_prev = self.get_max_score_for_player_in_state(1, experience.get_prev_state())
        player1_max_curr = self.get_max_score_for_player_in_state(1, experience.get_curr_state())
        player2_max_prev = self.get_max_score_for_player_in_state(2, experience.get_prev_state())
        player2_max_curr = self.get_max_score_for_player_in_state(2, experience.get_curr_state())

        if (verbose):
            print("player1: maxprev,maxcurr = "+str(player1_max_prev)+","+str(player1_max_curr))
            print("player2: maxprev,maxcurr = "+str(player2_max_prev)+","+str(player2_max_curr))

        # detect game restarts! if the maximum score for the current frame is 0, then the reward is ALWAYS 0.
        # This is prevent false rewards in cases where the scores get reset (i.e. player 1 has 10 points, but then
        # the game restarts, resetting player 1's score to 0. In this case, if we simply did reward = curr_max-prev_max,
        # we'd be assigning a negative reward when there shouldn't be!
        positive_reward = 0 if player1_max_curr == 0 else (player1_max_curr - player1_max_prev)
        negative_reward = 0 if player2_max_curr == 0 else (player2_max_curr - player2_max_prev)

        return positive_reward - negative_reward

    def get_max_score_for_player_in_state(self, player, state):
        scores = []
        for frame_num in state.get_frames():
            framedata = PongGameData(state.get_frame(frame_num))
            scores.append(int(framedata.get_score(player)))
        return max(scores)

