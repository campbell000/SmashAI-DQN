# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot.

PORT = 8081

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from cgi import parse_qs, escape
from dqn import SSB_DQN
import ast
import sys

verbose = False
if len(sys.argv) >= 2 and sys.argv[1] == "verbose":
    verbose = True
dqn_model = SSB_DQN(verbose=verbose)

def doTraining(data):
    del data['action'] # remove this field cause we don't need it anymore
    return dqn_model.get_prediction(data, do_train=True)

def doEval(data):
    del data['action'] # remove this field cause we don't need it anymore
    return dqn_model.get_prediction(data, do_train=False)

def doHello(data):
    return "HI FROM TENSORFLOW SERVER! THIS IS WHAT YOU SENT ME:\n"+str(data)

ACTION_MAP = [
    doTraining,
    doEval,
    doHello
]

# This function converts the POST data into a map
def get_form_data_from_request(req):
    form_data = {}
    fields = parse_qs(req)
    for k in fields:
        form_data[k.decode()] = ast.literal_eval(fields[k][0].decode())

    return form_data

# This class handles requests from bizhawk
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length) # <--- Gets the data itself
        fields = get_form_data_from_request(data)

        # Perform an action based on the "action" field in the POST data
        action_array = ACTION_MAP[fields["action"]](fields)

        # Convert the action array (a one hot vector indicating which action should be chosen
        response = transform_actions_for_client(action_array)

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

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()