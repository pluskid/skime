from .ctx import TopLevelContext, Context
from . import insns

class VM(object):

    def __init__(self):
        self.ctx = TopLevelContext(self)

    def run(self, proc):
        self.ctx = Context(self, proc)
        insns.run(self)
        return self.ctx.pop()
