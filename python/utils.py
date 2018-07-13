class Logger:
    def __init__(self, verbose=False):
        self.log_once_record = set()
        self.verbose = verbose

    def log_once(self, message):
        if message not in self.log_once_record:
            self.log_once_record.add(message)
            print(message)

    def log_verbose(self, message):
        if self.verbose:
            print(message)

    def log(self, message ):
        print(message)