# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot.

PORT = 8081
from http.server import BaseHTTPRequestHandler, HTTPServer
from dqn import SSB_DQN
import tensorflow as tf
from gamedata_parser import GameDataParser
import sys

# THESE VARIABLES SHOULD MATCH THE VARIABLES IN tensorflow-client.lua
TRAIN = 0
EVAL = 1
HELLO = 2

# This class handles requests from bizhawk
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    dqn_model = None
    started = False

    # This function handles requests from the client.
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length).decode() # <--- Gets the data itself
        game_data = GameDataParser.parse_client_data(data) # Parse the data into a map
        test_gamedata(game_data)
        action = "OK"
        fields = None
        response = None

        # If the action is train, train the bot and also retrieve a prediction for the client
        if action == TRAIN:
            action_array = self.dqn_model.get_prediction(fields, do_train=True)
            response = transform_actions_for_client(action_array)

        # Otherwise, simply get a prediction. Do not train the bot.
        elif action == EVAL:
            action_array = self.dqn_model.get_prediction(fields, do_train=False)
            response = transform_actions_for_client(action_array)
        else:
            print("Saying HELLO to the tensorflow client!")
            response = "HI FROM TENSORFLOW SERVER! THIS IS WHAT YOU SENT ME:\n"+str(data)

        # Write the response of the action to the client
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(response, "utf8"))

    # Silences logging
    def log_message(self, format, *args):
        return

def test_gamedata(data):
    for frame_num in sorted(data.get_current_state().get_frames()):
        print("For Frame "+str(frame_num))
        frame_data = data.get_current_state().get_frame(frame_num)
        for player_num in sorted(frame_data.get_players()):
            print("    For Player "+str(player_num))
            player_data = frame_data.get_player(player_num)
            for data_key in sorted(player_data.get_all_keys()):
                print("        "+data_key+": "+str(player_data.get(data_key)))

def transform_actions_for_client(action_arr):
    str_int_array = (str(int(e)) for e in action_arr)
    return ','.join(str_int_array)

def run():
    print('starting server...')
    config = tf.ConfigProto()
    config.gpu_options.allow_growth=True
    sess = tf.Session(config=config)

    with sess.as_default():
        verbose = False
        if len(sys.argv) >= 2 and sys.argv[1] == "verbose":
            verbose = True

        dqn_model = SSB_DQN(sess, verbose=verbose)

        # Run Server
        server_address = ('0.0.0.0', PORT)
        testHTTPServer_RequestHandler.dqn_model = dqn_model
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')
        httpd.serve_forever()

run()