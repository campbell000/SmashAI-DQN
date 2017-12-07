
DEATH_STATES = [0, 1, 2, 3] # TAKEN FROM gameConstants.lua!
class Rewarder:

    def __init__(self, life_multiplier=100, damage_multiplier=1):
        self.life_multiplier = life_multiplier
        self.damage_multiplier = damage_multiplier

    def state_is_death(self, state):
        if state in DEATH_STATES:
            return True
        else:
            return False

    # Assumes player 1 is the bot we want to train
    def calculate_reward(self, experience):
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

        return reward

    def is_terminal(self, experience):
        prev = experience[0]
        current = experience[1]
        return self.state_is_death(current["1state"]) and not self.state_is_death(prev["1state"])




