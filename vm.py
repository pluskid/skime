from ctx import Context
import insns

class VM(object):

    def __init__(self):
        self.ctx = None

    def run(self):
        insns.run(self)
        
    def call(self, proc, argc):
        ctx = Context(self.ctx, proc)
        self.ctx = ctx

    def ret(self):
        self.ctx = self.ctx.parent
