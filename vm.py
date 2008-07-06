from ctx import Context
import insns

class VM(object):

    def __init__(self):
        self.ctx = None

    def run(self):
        insns.run(self)
