# This file is the server that listens to requests from Bizhawk / Lua to train (and retrieve predictions for) the
# Super Smash Bros bot. In the diagrams, it is the "Learning Server"

PORT = 8081
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from cgi import parse_qs, escape
from dqn import SSB_DQN
import tensorflow as tf
import ast
import sys

# This class handles requests from bizhawk
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    dqn_model = None
    started = False

    # This function converts the POST data into a map
    def get_form_data_from_request(self, req):
        form_data = {}
        fields = parse_qs(req)
        for k in fields:
            form_data[k.decode()] = ast.literal_eval(fields[k][0].decode())

        return form_data

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length) # <--- Gets the data itself
        fields = self.get_form_data_from_request(data)
        response = None

        # Perform an action based on the "action" field in the POST data
        action = fields["action"]
        del fields['action'] # remove this field cause we don't need it anymore
        if action == 0:
            action_array = self.dqn_model.get_prediction(fields, do_train=True)
            response = transform_actions_for_client(action_array)
        else:
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

    sess = tf.Session()
    with sess.as_default():
        verbose = False
        if len(sys.argv) >= 2 and sys.argv[1] == "verbose":
            verbose = True

        dqn_model = SSB_DQN(sess, verbose=verbose)

        # Run Server
        server_address = ('127.0.0.1', PORT)
        testHTTPServer_RequestHandler.dqn_model = dqn_model
        httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
        print('running server...')
        httpd.serve_forever()

run()