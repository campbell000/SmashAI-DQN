from urllib.parse import urlparse
from urllib.parse import parse_qs
import ast

INITIAL_STATE_VALUE_INDEX = 1
INITIAL_PLAYER_VALUE_INDEX = 3

NUM_PLAYERS = 2
NUM_STATES = 2

class GameDataParser:
    # This function converts the POST data into a map with the following structure:
    # {
    #   "states" : [
    #      "players" : [
    #         "xp" : 23.3,
    #         "xv" : 2,
    #         ...
    #      ]
    #   ]
    # }
    #
    # The server is sending one or more game states, where each state contains various attributes about each player.
    def parse_client_data(req):
        game_data = [None] * NUM_STATES
        fields = parse_qs(req)

        # Get the action field and then remove it (it is not associated with a specific frame or player
        action = ast.literal_eval(fields["action"][0])
        del fields['action'] # remove this field cause we don't need it anymore

        #s23p1

        for full_key in fields:
            # Convert strings to strings, floats to floats, and ints to ints (everything comes back from parse_qs as a string).
            value = ast.literal_eval(fields[full_key][0])

            state = None
            player = None
            attr_name_start = 4

            if full_key[INITIAL_STATE_VALUE_INDEX + 1].isdigit():
                state = int(full_key[INITIAL_STATE_VALUE_INDEX:INITIAL_STATE_VALUE_INDEX+2]) - 1
                player = int(full_key[INITIAL_PLAYER_VALUE_INDEX + 1]) - 1
                attr_name_start = 5
            else:
                state = int(full_key[INITIAL_STATE_VALUE_INDEX]) - 1
                player = int(full_key[INITIAL_PLAYER_VALUE_INDEX]) - 1


            if game_data[state] == None:
                game_data[state] = [dict() for i in range(NUM_PLAYERS)]

            key = full_key[attr_name_start:]
            game_data[state][player][key] = value

        return action, game_data