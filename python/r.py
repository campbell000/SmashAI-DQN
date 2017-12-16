import numpy as np

def zipWith(f, *sequences):
    return [f(*args) for args in zip(*sequences)]
def processDamages(percents):
    return np.array(zipWith(lambda prev, next: max(next-prev, 0), percents, percents[1:]))
def isDying(player):
    # see https://docs.google.com/spreadsheets/d/1JX2w-r2fuvWuNgGb6D3Cs4wHQKLFegZe2jhbBuIhCG8/edit#gid=13
    return player.action_state == 1
a = [20, 30, 40, 50]

print(processDamages(a))