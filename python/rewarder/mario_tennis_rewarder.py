from rewarder.rewarder import *
from gameprops.gameprops import *
from gameprops.pong_gameprops import *
from gamedata_parser import *

class MarioTennisRewarder(AbstractRewarder):

    def __init__(self):
        super(AbstractRewarder, self).__init__()
        self.serve_reward = 0.01

    def experience_is_terminal(self, experience):
        reward = self.calculate_reward(experience)
        return reward == -1 or reward == 1

    # Take the difference between the max scores for prev/current state. Each state could have multiple frames; we're
    # only concerned with the difference between the maxes of each state's frames
    # NOTE: reward is player 1-centric!
    def calculate_reward(self, experience, verbose=False):
        reward = 0
        player1_max_prev = self.get_max_score_for_player_in_state(1, experience.get_prev_state())
        player1_max_curr = self.get_max_score_for_player_in_state(1, experience.get_curr_state())
        player2_max_prev = self.get_max_score_for_player_in_state(2, experience.get_prev_state())
        player2_max_curr = self.get_max_score_for_player_in_state(2, experience.get_curr_state())

        # give player small reward for serving. Otherwise they just hold onto the ball and do nothing
        p1_prev_serving = self.is_player_serving(1, experience.get_prev_state())
        p1_curr_serving = self.is_player_serving(1, experience.get_curr_state())
        p2_prev_serving = self.is_player_serving(2, experience.get_prev_state())
        p2_curr_serving = self.is_player_serving(2, experience.get_curr_state())

        if p1_prev_serving and not p1_curr_serving:
            reward = reward + self.serve_reward

        # detect game restarts! if the maximum score for the current frame is 0, then the reward is ALWAYS 0.
        # This is prevent false rewards in cases where the scores get reset (i.e. player 1 has 10 points, but then
        # the game restarts, resetting player 1's score to 0. In this case, if we simply did reward = curr_max-prev_max,
        # we'd be assigning a negative reward when there shouldn't be!
        positive_reward = 0 if player1_max_curr == 0 else (player1_max_curr - player1_max_prev)
        negative_reward = 0 if player2_max_curr == 0 else (player2_max_curr - player2_max_prev)

        # Make sure we're not rewarding points due to restarting to a better state
        #TODO CHECK THIS BETTER
        #TODO CHECK THIS BETTER
        if self.check_if_we_restarted(experience.get_curr_state()) or self.check_if_we_restarted(experience.get_prev_state())\
                or (p1_curr_serving or p2_curr_serving):
            positive_reward = 0
            negative_reward = 0

        reward = reward + (positive_reward - negative_reward)
        return reward

    def is_player_serving(self, player, state):
        is_serving = []
        for frame_num in state.get_frames():
            data = state.get_frame(frame_num)
            is_serving.append(int(data.get(str(player)+"srv")))

        return min(is_serving) == 1

    def get_max_score_for_player_in_state(self, player, state):
        scores = []
        for frame_num in state.get_frames():
            data = state.get_frame(frame_num)
            scores.append(int(data.get(str(player)+"score")))
        return max(scores)

    def check_if_we_restarted(self, state):
        scores = []
        for frame_num in state.get_frames():
            data = state.get_frame(frame_num)
            scores.append(int(data.get("restarted")))
        return max(scores)
