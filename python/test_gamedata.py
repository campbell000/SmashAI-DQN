test_data = "s1p1is_in_air=1&s1p2state=156&s1p1state=26&s1p2ya=0&s1p2is_in_air=0&s1p2state_frame=29&s1p2yv=0&s1p1damage=35&s1p2yp=0&s1p2shield_recovery_time=733&s1p1yv=-58&s1p2shield_size=55&s1p2damage=0&s1p1xv=37.599975585938&s1p1ya=0&s1p1shield_recovery_time=0&s1p2character=9&s1p1shield_size=55&s1p2direction=1&s1p1direction=1&s1p1yp=-877.99993896484&s1p1xp=3359.3442382813&s1p1state_frame=25&s1p1jumps_remaining=1&s1p2jumps_remaining=2&s1p2xa=-3.2858030796051&s1p2xv=-3.2858030796051&s1p2xp=1353.8891601563&s1p1xa=28&s1p1character=6&s2p1is_in_air=1&s2p2state=156&s2p1state=26&s2p2ya=0&s2p2is_in_air=0&s2p2state_frame=30&s2p2yv=0&s2p1damage=35&s2p2yp=0&s2p2shield_recovery_time=733&s2p1yv=-58&s2p2shield_size=55&s2p2damage=0&s2p1xv=37.199974060059&s2p1ya=0&s2p1shield_recovery_time=0&s2p2character=9&s2p1shield_size=55&s2p2direction=1&s2p1direction=1&s2p1yp=-935.99993896484&s2p1xp=3396.5441894531&s2p1state_frame=26&s2p1jumps_remaining=1&s2p2jumps_remaining=2&s2p2xa=-2.6694395542145&s2p2xv=-2.6694395542145&s2p2xp=1356.0924072266&s2p1xa=28&s2p1character=6&s3p1is_in_air=1&s3p2state=156&s3p1state=26&s3p2ya=0&s3p2is_in_air=0&s3p2state_frame=31&s3p2yv=0&s3p1damage=35&s3p2yp=0&s3p2shield_recovery_time=733&s3p1yv=-58&s3p2shield_size=55&s3p2damage=0&s3p1xv=36.79997253418&s3p1ya=0&s3p1shield_recovery_time=0&s3p2character=9&s3p1shield_size=55&s3p2direction=1&s3p1direction=1&s3p1yp=-993.99993896484&s3p1xp=3433.3442382813&s3p1state_frame=27&s3p1jumps_remaining=1&s3p2jumps_remaining=2&s3p2xa=-2.4768187999725&s3p2xv=-2.4768187999725&s3p2xp=1358.4869384766&s3p1xa=28&s3p1character=6&s4p1is_in_air=1&s4p2state=156&s4p1state=26&s4p2ya=0&s4p2is_in_air=0&s4p2state_frame=32&s4p2yv=0&s4p1damage=35&s4p2yp=0&s4p2shield_recovery_time=733&s4p1yv=-58&s4p2shield_size=55&s4p2damage=0&s4p1xv=36.399971008301&s4p1ya=0&s4p1shield_recovery_time=0&s4p2character=9&s4p1shield_size=55&s4p2direction=1&s4p1direction=1&s4p1yp=-1052&s4p1xp=3469.744140625&s4p1state_frame=28&s4p1jumps_remaining=1&s4p2jumps_remaining=2&s4p2xa=-2.7073607444763&s4p2xv=-2.7073607444763&s4p2xp=1360.6494140625&s4p1xa=28&s4p1character=6&action=0"

from gamedata_parser import GameDataParser

action, data = GameDataParser.parse_client_data(test_data)
print(data)
for state_index, state in enumerate(data):
    for player_index, player in enumerate(state):
        for attr in player:
            form_datum = ("s"+str(state_index+1)+"p"+str(player_index+1)+""+attr+"="+str(player[attr]))
            print(form_datum)
            if form_datum not in test_data:
                form_datum = ("s"+str(state_index+1)+"p"+str(player_index+1)+""+attr+"=-"+str(player[attr]))

            if form_datum not in test_data:
                print("WHOA, THE FORM DATA TO GAME DATA CONVERSION PROCESS IS WRONG!")
                print(form_datum)
                exit(-127)