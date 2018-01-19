# This class is responsible for calculating the rewards for a previous state / current state pair.

DEATH_STATES = [0, 1, 2, 3] # TAKEN FROM gameConstants.lua!
NOTHING_REWARD = 0.000000 # Incentivize it to NOT die


class Rewarder:

    def __init__(self, num_frames_per_state, sample_rate, life_multiplier=1, damage_multiplier=0.001):
        self.sample_rate = sample_rate
        self.num_frames_per_state = num_frames_per_state
        self.life_multiplier = life_multiplier
        self.damage_multiplier = damage_multiplier

    # Returns true if the state represents a KO state
    def state_is_death(self, state):
        if state in DEATH_STATES:
            return True
        else:
            return False

    def player_died(self, experience, player):
        prev = experience[0]
        current = experience[1]

        # Check if the player did NOT die in the previous state. If they did, they we are NOT considering them dead,
        # since we are only counting the death reward ONCE, and that's when they immediately die.
        for state in prev:
            state_value = state[player]["state"]
            if self.state_is_death(state_value):
                return 0

        # If the player hasn't died in the previous state, and there IS a death in the current state, then consider them dead
        for state in current:
            state_value = state[player]["state"]
            if self.state_is_death(state_value):
                return 1

        # If they didn't die in either the previous state or current state, then they ain't dead.
        return 0

    # This method calculates the reward for an experience. It assumes that player 1 is the bot we want to train
    def calculate_reward(self, experience, for_current_verbose=False):
        prev = experience[0]
        current = experience[1]

        # Calculate damage dealt / taken differentials. Use the damage from the LAST frames for the previous/current states
        # TODO WE NEED TO NOT HARD CODE THE FACT THAT PLAYER 1 IS THE BOT.
        last_frame_idx = self.num_frames_per_state - 1
        damage_taken = current[last_frame_idx][0]["damage"] - prev[last_frame_idx][0]["damage"]
        damage_dealt = current[last_frame_idx][1]["damage"] - prev[last_frame_idx][1]["damage"]

        # Do NOT reward or punish the bot when their damage counter gets reset.
        if damage_taken < 0:
            damage_taken = 0
        if damage_dealt < 0:
            damage_dealt = 0

        damage_reward = damage_dealt - damage_taken

        # Calculate kills / deaths. Since death states occur for a few frames, check if death ocurred right after not-death ocurred.
        is_bot_dead = self.player_died(experience, 0)
        is_opponent_dead = self.player_died(experience, 1)
        death_reward = is_opponent_dead - is_bot_dead

        # Calculate final reward by adding the damage-related rewards to the death-related rewards
        reward = (damage_reward * self.damage_multiplier)
        reward += (death_reward * self.life_multiplier)

        # If the bot did not take damage and did not die, give it a little bit of a reward
        if damage_taken == 0 and is_bot_dead == 0:
            reward += NOTHING_REWARD

        if for_current_verbose:
            print("REWARDS FOR CURRENT experience: ")
            print("damage_dealt: "+str(damage_dealt))
            print("damage_taken: "+str(damage_taken))
            print("is_bot_dead: "+str(is_bot_dead))
            print("is_opponent_dead: "+str(is_opponent_dead))
            print("TOTAL REWARD: "+str(reward))

        return reward

    # This method returns true if the bot we're training gets KO'd
    def bot_killed_opponent(self, experience):
        return self.player_died(experience, 1)

    # This method returns true if the bot's opponent gets KO'd
    def opponent_killed_bot(self, experience):
        return self.player_died(experience, 0)

    # This method retrurns true if the current experience is a terminal state
    def is_terminal(self, experience):
        return self.opponent_killed_bot(experience)




