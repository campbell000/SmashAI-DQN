# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot.

PORT = 8081
from http.server import BaseHTTPRequestHandler, HTTPServer
from dqn import SSB_DQN
import tensorflow as tf
from gamedata_parser import GameDataParser
from gameprops.gameprops import *
from gameprops.pong_gameprops import *
from gameprops.ssb_gameprops import *
from shared_constants import Constants
from gamedata_parser import *
from rewarder.rewarder import *
from rewarder.pong_rewarder import *
from rewarder.ssb_rewarder import *
from rewarder.dumb_ssb_rewarder import *
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

        # If the action is train, train the bot and also retrieve a prediction for the client
        if game_data.get_client_action() == TRAIN:
            action_index = self.dqn_model.get_prediction(game_data, do_train=True)
            response = str(action_index)
        elif game_data.get_client_action() == EVAL:
            action_index = self.dqn_model.get_prediction(game_data, do_train=False)
            response = str(action_index)
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

        ## PARAMS FOR SSB. COMMENT OUT FOR SOMETHING ELSE
        gameprops = PongGameProps()
        rewarder = PongRewarder()

        dqn_model = SSB_DQN(sess, gameprops, rewarder, verbose=verbose)

        # Run Server
        server_address = ('0.0.0.0', PORT)
        testHTTPServer_RequestHandler.dqn_model = dqn_model
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')
        httpd.serve_forever()

def test():
    print('starting server...')
    config = tf.ConfigProto()
    config.gpu_options.allow_growth=True
    sess = tf.Session(config=config)

    with sess.as_default():
        ## PARAMS FOR PONG. COMMENT OUT FOR SOMETHING ELSE
        gameprops = SSBGameProps()
        rewarder = SSBRewarder()

        dqn_model = SSB_DQN(sess, gameprops, rewarder)
        i = 0
        while True:
            i = i + 1
            dqn_model.update_random_prob()
            print("iteration: "+str(i)+", prob: "+str(dqn_model.get_random_action_prob()))

run()
#test()