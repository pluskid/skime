from prim import load_primitives

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

    def find_local(self, name):
        """\
        Find index of local variable in the context.
        Raise ValueError if not found.
        """
        return self.proc.locals.index(name)
        
    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def top(self):
        return self.stack[-1]


class TopLevelContext(object):
    "VM top level context."
    def __init__(self, vm):
        self.vm = vm
        self.prev = None
        self.ip = 1 # ip always greater than len(bytecode)
        self.bytecode = []

        self.locals = []
        self.local_maps = {}

        load_primitives(self)

    def find_local(self, name):
        idx = self.local_maps[name]
        if idx:
            return idx
        raise ValueError("%s not found" % name)

    def add_local(self, name, value):
        idx = len(self.locals)
        self.locals.append(value)
        self.local_maps[name] = idx
