from abc import ABC

class Driver(ABC):
    def configure(self, config):
        pass

    def setup(self):
        pass

    def push(self, job ):
        pass