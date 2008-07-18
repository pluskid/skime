from .prim import load_primitives

class Context(object):
    def __init__(self, vm, proc):
        self.vm = vm
        self.prev = vm.ctx
        self.proc = proc
        
        self.ip = 0
        self.bytecode = proc.bytecode
        self.stack = []
        self.locals = [None for x in proc.locals]

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

    def get_local_name(self, idx):
        """\
        Get the name of a local variable from the index. Used
        in debugging.
        """
        return self.proc.locals[idx]
        
    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def pop_n(self, n):
        del self.stack[-n:]
    def top(self, idx=1):
        return self.stack[-idx]


class TopLevelContext(Context):
    "VM top level context."
    def __init__(self, vm):
        self.vm = vm
        self.prev = None
        self.ip = 1 # ip always greater than len(bytecode)
        self.bytecode = []

        self.locals = []
        self.local_names = []
        self.local_maps = {}
        self.stack = []

        load_primitives(self)

    def parent_get(self):
        return None
    def parent_set(self, val):
        raise AttributeError("attribute 'parent' is read only")
    parent = property(parent_get, parent_set)

    def find_local(self, name):
        """\
        Find index of local variable in the context.
        Raise ValueError if not found.
        """
        idx = self.local_maps.get(name)
        if idx is not None:
            return idx
        raise ValueError("%s not found" % name)

    def get_local_name(self, idx):
        """\
        Get the name of a local variable from the index. Used
        in debugging.
        """
        return self.local_names[idx]
        
    def add_local(self, name, value):
        idx = len(self.locals)
        self.locals.append(value)
        self.local_names.append(name)
        self.local_maps[name] = idx
