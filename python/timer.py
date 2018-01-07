import time
class Timer:
    def __init__(self):
        self.start_time = None

    def set_start_time(self):
        self.start_time = time.monotonic()

    def get_elapsed_ms(self):
        return time.monotonic() - self.start_time