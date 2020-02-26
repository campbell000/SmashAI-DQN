from rewarder.rewarder import *

DEATH_STATES = list(range(9)) # TAKEN FROM gameConstants.lua!
STAGE_SAFE_BOUNDARY = 2250
class SSBRewarder(AbstractRewarder):
    def __init__(self, use_grounded=True, use_stay_on_stage=True):
        self.give_damage_multiplier = 0.07
        self.take_damage_multiplier = 0.03
        self.life_multiplier = 1
        self.death_multiplier = 5
        self.living_multiplier = 0.0001
        self.is_grounded_multiplier = 0.000001
        self.stay_on_stage_multiplier = 0.000001
        self.use_grounded = use_grounded
        self.use_stay_on_stage = use_stay_on_stage

        print("SSB REWARDER: ")
        print("  BOT DEALS DAMAGE MULTIPLIER: "+str(self.give_damage_multiplier))
        print("  BOT takes DAMAGE MULTIPLIER: "+str(self.take_damage_multiplier))
        print("  LIFE MULTIPLIER: "+str(self.life_multiplier))
        print("  LIVING MULTIPLIER: "+str(self.living_multiplier))
        print("  GROUNDED REWARD: "+str(self.use_grounded))
        print("  STAGE REWARD: "+str(self.use_stay_on_stage))

    def state_is_death(self, state):
        if state in DEATH_STATES:
            return True
        else:
            return False

    def should_not_reward_small(self, experience):
        current = experience.get_curr_state()

        # If the player hasn't died in the previous state, and there IS a death in the current state, then consider them dead
        for frame_idx in current.get_frames():
            state_value = current.get_frame(frame_idx).get(str(1)+"state")
            if state_value in DEATH_STATES:
                return True
        return False

    def player_died(self, experience, player):
        prev = experience.get_prev_state()
        current = experience.get_curr_state()

        # Check if the player did NOT die in the previous state. If they did, then we are NOT considering them dead,
        # since we are only counting the death reward ONCE, and that's when they immediately die.
        for frame_idx in prev.get_frames():
            state_value = prev.get_frame(frame_idx).get(str(player)+"state")
            if self.state_is_death(state_value):
                return 0

        # If the player hasn't died in the previous state, and there IS a death in the current state, then consider them dead
        for frame_idx in current.get_frames():
            state_value = current.get_frame(frame_idx).get(str(player)+"state")
            if self.state_is_death(state_value):
                return 1

        # If they didn't die in either the previous state or current state, then they ain't dead.
        return 0

    # This method calculates the reward for an experience. It assumes that player 1 is the bot we want to train
    def calculate_reward(self, experience, for_current_verbose=False):
        prev = experience.get_prev_state()
        current = experience.get_curr_state()

        # Calculate damage dealt / taken differentials. Use the damage from the LAST frames for the previous/current states
        # TODO WE NEED TO NOT HARD CODE THE FACT THAT PLAYER 1 IS THE BOT.
        last_frame_idx = current.get_num_frames() - 1
        damage_taken = current.get_frame(last_frame_idx).get("1dmg") - prev.get_frame(last_frame_idx).get("1dmg")
        damage_dealt = current.get_frame(last_frame_idx).get("2dmg") - prev.get_frame(last_frame_idx).get("2dmg")

        # Do NOT reward or punish the bot when their damage counter gets reset.
        if damage_taken < 0:
            damage_taken = 0
        if damage_dealt < 0:
            damage_dealt = 0

        damage_reward = damage_dealt - damage_taken

        # Calculate kills / deaths. Since death states occur for a few frames, check if death ocurred right after not-death ocurred.
        is_bot_dead = self.player_died(experience, 1)
        is_opponent_dead = self.player_died(experience, 2)
        death_reward = (is_opponent_dead * self.life_multiplier) - (is_bot_dead * self.death_multiplier)

        # Calculate final reward by adding the damage-related rewards to the death-related rewards
        reward = (damage_dealt * self.give_damage_multiplier)
        reward -= (damage_taken * self.take_damage_multiplier)
        reward += death_reward

        # If the bot did not take damage and did not die, give it a little bit of a reward
        #if damage_taken == 0 and is_bot_dead == 0:
        #    reward += self.living_multiplier

        # Being on the ground is generally safer
        if not self.should_not_reward_small(experience):
            if self.use_grounded:
                is_in_air = current.get_frame(last_frame_idx).get("1is_air")
                if is_in_air == 0:
                    reward += self.is_grounded_multiplier

            # Staying within the stage bounds is generally safer
            if self.use_stay_on_stage:
                if abs(current.get_frame(last_frame_idx).get("1xp")) > STAGE_SAFE_BOUNDARY:
                    reward -= self.stay_on_stage_multiplier
                else:
                    reward += self.stay_on_stage_multiplier

        if for_current_verbose:
            print("REWARDS FOR CURRENT experience: ")
            print("damage_dealt: "+str(damage_dealt))
            print("damage_taken: "+str(damage_taken))
            print("is_bot_dead: "+str(is_bot_dead))
            print("is_opponent_dead: "+str(is_opponent_dead))
            print("is_in_air: "+str(is_opponent_dead))
            print("TOTAL REWARD: "+str(reward))

        return reward

    # This method returns true if the bot we're training gets KO'd
    def bot_killed_opponent(self, experience):
        return self.player_died(experience, 2)

    # This method returns true if the bot's opponent gets KO'd
    def opponent_killed_bot(self, experience):
        return self.player_died(experience, 1)

    # This method retrurns true if the current experience is a terminal state
    def experience_is_terminal(self, experience):
        return self.opponent_killed_bot(experience) == 1

    def should_record_reward_in_log(self, experience):
        return self.experience_is_terminal(experience)

    def get_reward_for_log(self, experience):
        return self.calculate_reward(experience)