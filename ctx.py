
class Context(object):
    def __init__(self, vm, proc):
        self.vm = vm
        self.prev = vm.ctx
        self.proc = proc
        
        self.ip = 0
        self.bytecode = proc.bytecode
        self.stack = []
        self.locals = map(lambda x: None, proc.locals)

    def parent_get(self):
        return self.proc.lexical_parent
    def parent_set(self, val):
        raise AttributeError("attribute 'parent' is read only")
    parent = property(parent_get, parent_set)
        
    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def top(self):
        return self.stack[-1]
