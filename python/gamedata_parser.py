from urllib.parse import urlparse
from urllib.parse import parse_qs
import re
import ast

CURRENT_STRING = "c"
PREVIOUS_STRING = "p"

class GameDataParser:
    """
    A class to parse data received from the client. The data structure that this class produces is as follows:
    - GameData:
        - Current State:
            - Frame 0:
                - Player 1:
                    - Data....
                - Player 2:
                    - Data...
            - Frame 1:
                ...
        - Previous State:
            - Frame 0:...
            - Frame 1:...

    The intent is to model the following: every GameData object has a "state". A state represents a current sampling
    point for the machine learning algorithms. The "current" state is the state that we need to make a decision for,
    while the "previous" state is the state that we JUST made a decision for. Each client keeps track of its current
    and previous state.

    Each state is comprised of one or more "frames". A "frame" is a specific point in time in the game state. A frame
    contains data for multiple players. Each player knows about it's own state (x/y coords, action, character, etc).
    """

    def parse_client_data(req):
        map = {}
        fields = parse_qs(req)

        # Get the action field and then remove it (it is not associated with a specific frame or player
        action = ast.literal_eval(fields["action"][0])
        del fields['action'] # remove this field cause we don't need it anymore

        for key in fields:
            state_type = "current" if key.startswith(CURRENT_STRING) else "previous"
            value = ast.literal_eval(fields[key][0]) # Everything returned by parse_qa is returned as a array of strings
            frame, player, dataKey = re.findall('\[(.*?)\]',key)
            frame = int(frame)
            player = int(player) - 1 # the client starts at 1

            # Create GameDataState for the state if it doesn't exist.
            if state_type not in map:
                map[state_type] = GameDataState()

            game_state = map[state_type]
            if game_state.get_frame(frame) == False:
                game_state.add_frame(frame)

            game_frame = game_state.get_frame(frame)
            if (game_frame.get_player(player)) == False:
                game_frame.add_player(player)

            game_player = game_frame.get_player(player)
            game_player.add(dataKey, value)

        return GameData(map, action)

class GameData:
    def __init__(self, map, action):
        self.map = map
        self.action = action

    def get_current_state(self):
        return self.map["current"]

    def get_previous_state(self):
        return self.map["previous"]

    def get_client_action(self):
        return self.action

    def get_num_frames_per_state(self):
        num_frames_for_current = self.get_current_state().get_num_keys()
        num_frames_for_prev = self.get_previous_state().get_num_keys()
        if num_frames_for_current != num_frames_for_prev:
            raise Exception("WHOA, THE PREVOUS AND CURRENT STATE HAVE DIFFERENT NUMBER OF FRAMES!")

        return num_frames_for_current

class GameDataState:
    def __init__(self):
        self.frames = {}

    def add_frame(self, frameIndex):
        self.frames[frameIndex] = GameDataFrame()

    def get_frame(self, frameIndex):
        if frameIndex in self.frames:
            return self.frames[frameIndex]
        else:
            return False

    def get_num_frames(self):
        return len(self.frames.keys())

    def get_frames(self):
        return self.frames.keys()

class GameDataFrame:
    def __init__(self):
        self.players = {}

    def add_player(self, playerID):
        self.players[playerID] = GamePlayerData()

    def get_player(self, playerID):
        if  playerID in self.players:
            return self.players[playerID]
        else:
            return False

    def get_players(self):
        return self.players.keys()

class GamePlayerData:
    def __init__(self):
        self.map = {}

    def add(self, key, value):
        self.map[key] = value

    def get(self, key):
        return self.map[key]

    def get_all_keys(self):
        return self.map.keys()



