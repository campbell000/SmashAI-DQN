# Add numbers here that are shared between lua and python!
import configparser

class Constants:
    NUM_FRAMES_PER_STATE = 2

class SharedConstants:
    def __init__(self):
        self.game_map = {}
        with open('../shared_constants.properties', 'r') as file:
            for line in file.readlines():
                game = line.split('.')[0]
                property = line.split('.')[1]
                prop_name = property.split('=')[0]
                prop_val = int(property.split('=')[1])

                if game not in self.game_map:
                    self.game_map[game] = {}

                self.game_map[game][prop_name] = prop_val

    def get_prop_val(self, game, prop_name):
        return self.game_map[game][prop_name]
