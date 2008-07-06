
class Context(object):
    def __init__(self, vm, proc):
        self.vm = vm
        self.parent = vm.ctx
        self.proc = proc
        
        self.ip = 0
        self.bytecode = proc.bytecode
        self.stack = []
        self.locals = map(lambda x: None, proc.locals)

    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def top(self):
        return self.stack[-1]
