from .prim import load_primitives

class Context(object):
    def __init__(self, form, env, parent=None):
        self.form = form
        self.env = env
        self.vm = env.vm
        self.parent = parent

        self.ip = 0
        self.bytecode = form.bytecode
        self.stack = []

    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def pop_n(self, n):
        del self.stack[-n:]
    def top(self, idx=1):
        return self.stack[-idx]

