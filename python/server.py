# This file is the server that listens to requests from Bizhawk / Lua. To run it, simply run it as a normal python
# program (i.e. python server.py)
#!/usr/bin/env python

PORT = 8081

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from cgi import parse_qs, escape
from dqn import DQN

dqn_model = DQN()

def doTraining(data):
    return dqn_model.train(data)

def doEval(data):
    return dqn_model.eval(data)

def doHello(data):
    return "HI FROM TENSORFLOW SERVER!"

action_map = {
    "train" : doTraining,
    "eval"  : doEval,
    "hello" : doHello
}

# This function converts the POST data into a map
def get_form_data_from_request(req):
    form_data = {}
    fields = parse_qs(req)
    for k in fields:
        form_data[k.decode()] = fields[k][0].decode()
    return form_data

# This class handles requests from bizhawk
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print( "incomming http: ", self.path )
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        data = self.rfile.read(content_length) # <--- Gets the data itself
        fields = get_form_data_from_request(data)
        print(fields)

        # Perform an action based on the "action" field in the POST data
        response = action_map[fields["action"]](fields)

        # Write the response of the action to the client
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(response, "utf8"))

def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()