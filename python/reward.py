# This class is responsible for calculating the rewards for a previous state / current state pair.

DEATH_STATES = [0, 1, 2, 3] # TAKEN FROM gameConstants.lua!
NOTHING_REWARD = 0.000 # Incentivize it to NOT die
class Rewarder:

    def __init__(self, life_multiplier=1, damage_multiplier=0.001):
        self.life_multiplier = life_multiplier
        self.damage_multiplier = damage_multiplier

    # Returns true if the state represents a KO state
    def state_is_death(self, state):
        if state in DEATH_STATES:
            return True
        else:
            return False

    # This method calculates the reward for an experience. It assumes that player 1 is the bot we want to train
    def calculate_reward(self, experience, for_current_verbose=False):
        prev = experience[0]
        current = experience[1]

        # Calculate damage dealt / taken differentials
        damage_taken = current["1damage"] - prev["1damage"]
        damage_dealt = current["2damage"] - prev["2damage"]
        damage_reward = damage_dealt - damage_taken

        # Calculate kills / deaths. Since death states occur for a few frames, check if death ocurred right after not-death ocurred.
        is_bot_dead = 1 if self.state_is_death(current["1state"]) and not self.state_is_death(prev["1state"]) else 0
        is_opponent_dead = 1 if self.state_is_death(current["2state"]) and not self.state_is_death(prev["2state"]) else 0
        death_reward = is_opponent_dead - is_bot_dead

        # Calculate final reward by adding the damage-related rewards to the death-related rewards
        reward = 0
        reward += (damage_reward * self.damage_multiplier)
        reward += (death_reward * self.life_multiplier)

        # THIS GIVES THE BOT A LITTLE BIT OF MOTIVATION TO STAY ALIVE
        if reward == 0 and (damage_dealt == 0 and damage_taken == 0):
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
        prev = experience[0]
        current = experience[1]
        return self.state_is_death(current["2state"]) and not self.state_is_death(prev["2state"])

    # This method returns true if the bot's opponent gets KO'd
    def opponent_killed_bot(self, experience):
        return self.is_terminal(experience)

    # This method retrurns true if the current experience is a terminal state
    def is_terminal(self, experience):
        prev = experience[0]
        current = experience[1]
        return self.state_is_death(current["1state"]) and not self.state_is_death(prev["1state"])




