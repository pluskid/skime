from ctx import Context
import insns

class VM(object):

    def __init__(self):
        self.stack = []
        self.ctx = None

    def run(self):
        insns.run(self)
        
    def call(self, proc, argc):
        ctx = Context(self.ctx, proc)
        self.ctx = ctx

    def ret(self):
        self.ctx = self.ctx.parent

    def stk_pop(self):
        return self.stack.pop()
    def stk_top(self):
        return self.stack[-1]
    def stk_fetch(self, n):
        return self.stack[n]
    def stk_push(self, obj):
        self.stack.append(obj)
