# This file is meant to perform a sanity check on the DQN logic to make sure everything is working right.

from dqn import SSB_DQN
from urllib.parse import urlparse
from cgi import parse_qs, escape
import ast

NUM_ITERATIONS = 50010
NUM_TO_SKIP = 50000
STOP_AFTER_EACH_ITERATION = True

def get_form_data_from_request(req):
    form_data = {}
    fields = parse_qs(req)
    for k in fields:
        form_data[k] = ast.literal_eval(fields[k][0])
    return form_data

mock_client_data = ("2xv=0&2state=166&1state=10&1damage=2&2shield_recovery_time=0&2yv=0&1yv=0"
                    "&2shield_size=55&2damage=2&1xv=0&1ya=0&1shield_recovery_time=0&2character=9&1shield_size=55"
                    "&2direction=-1&1direction=-1&2xp=636.94964599609&1xp=-6.75&2ya=0&1jumps_remaining=2&2jumps_remaining=2"
                    "&2yp=0&2xa=0&1xa=0&1character=6&1damage=0&2damage=0&1yp=" # increment the last character so we know what's going on.'

                    )

dqn = SSB_DQN(verbose=False)
a = True

for i in range(0, NUM_ITERATIONS):
    mock_data = mock_client_data + str(i) # add i to the very end so that we know what state we're on
    mock_parsed_data = get_form_data_from_request(mock_data)

    action = dqn.get_prediction(mock_parsed_data, do_train=True)
    if i >= NUM_TO_SKIP:
        dqn.set_verbose(True)
        input("Press Enter to continue...")
        print("\n\n")
    elif a:
        print("Working through initial iterations...")
        a = False


