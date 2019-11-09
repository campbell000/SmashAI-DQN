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
                key1: val1
                key2: val2
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
        clientID = fields["clientID"][0]
        del fields['clientID'] # remove this field cause we don't need it anymore

        # We're using maps to store the data, rather than arrays, because the data is not guaranteed to be in order.
        # For example, frame 1's data might be interspersed with frame 0's data.
        for key in fields:
            state_type = "current"
            value = ast.literal_eval(fields[key][0]) # Everything returned by parse_qa is returned as a array of strings
            frame, dataKey = re.findall('\[(.*?)\]',key)
            frame = int(frame)

            # Create GameDataState for the state if it doesn't exist.
            if state_type not in map:
                map[state_type] = GameDataState()

            game_state = map[state_type]
            if game_state.get_frame(frame) == False:
                game_state.add_frame(frame)

            game_frame = game_state.get_frame(frame)
            game_frame.add(dataKey, value)

        return GameData(map, action, clientID, req)

class GameData:
    def __init__(self, map, action, clientID, rawData):
        self.map = map
        self.action = action
        self.clientID = clientID
        self.raw_data = rawData

    def get_current_state(self):
        return self.map["current"]

    def get_client_action(self):
        return self.action

    def get_num_frames_per_state(self):
        num_frames_for_current = self.get_current_state().get_num_keys()
        return num_frames_for_current

    def get_clientID(self):
        return self.clientID

    def get_raw_data(self):
        return self.raw_data

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

    # Returns keys for frames, in order
    def get_frames(self):
        return sorted(self.frames.keys())

class GameDataFrame:
    def __init__(self):
        self.map = {}

    def add(self, key, value):
        self.map[key] = value

    def set(self, key, value):
        self.add(key, value)

    def get(self, key):
        return self.map[key]

    def get_all_keys(self):
        return self.map.keys()

class PongGameData:

    def __init__(self, framedata):
        self.framedata = framedata

    def get_score(self, player):
        return self.framedata.get(str(player)+"score")

    def get_paddle_y_pos(self, player):
        return self.framedata.get(str(player)+"y")

    def get_ball_x_pos(self):
        return self.framedata.get("ballx")

    def get_ball_y_pos(self):
        return self.framedata.get("bally")



