from rewarder.rewarder import *
from gameprops.gameprops import *
from gamedata_parser import *

class PongRewarder(Rewarder):

    def __init__(self, num_frames_per_state):
        super(Rewarder, self).__init__(num_frames_per_state)

    # the experience is termainl if one player has '10' in the current state (any frame).
    def experience_is_terminal(self, experience):
        current_state = experience.get_current_state()
        for frame_num in current_state.get_frames()
            framedata = PongGameData(current_state.get_frame(frame_num))
            player1_score = framedata.get_score(1)
            player2_score = framedata.get_score(2)
            if player1_score == 10 or player2_score == 10:
                return True
        return False

    # Take the difference between the max scores for prev/current state. Each state could have multiple frames; we're
    # only concerned with the difference between the maxes of each state's frames
    # NOTE: reward is player 1-centric!
    def calculate_reward(self, experience):
        player1_max_prev = self.get_max_score_for_player_in_state(1, experience.get_previous_state())
        player1_max_curr = self.get_max_score_for_player_in_state(1, experience.get_current_state())
        player2_max_prev = self.get_max_score_for_player_in_state(2, experience.get_previous_state())
        player2_max_curr = self.get_max_score_for_player_in_state(2, experience.get_current_state())

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
            framedata = PongGameData(current_state.get_frame(frame_num))
            scores.append(int(framedata.get_score(player)))
        return max(scores)

