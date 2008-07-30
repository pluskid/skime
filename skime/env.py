class Location(object):
    """\
    A location of a variable, including the Environment object and
    the index in it.
    """
    __slots__ = ('env', 'idx')
    
    def __init__(self, env, idx):
        self.env = env
        self.idx = idx

    def __eq__(self, other):
        "Test if two Location object refer to the same location."
        return isinstance(other, Location) and \
               self.idx == other.idx and \
               self.env is other.env

    # Python rocks! Just Keep It Simple and verboSe.
    # When you defined __eq__, please also define __ne__ or
    # else != will compare by the memory address of your
    # objects
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '<Location idx=%s, env=%s>' % (self.idx, self.env)

class Undef(object):
    undef = None
    def __new__(cls):
        if cls.undef is None:
            cls.undef = object.__init__(cls)
        return cls.undef
        
    def __repr__(self):
        return '<undef>'
    def __str__(self):
        return '<undef>'

class Environment(object):
    """\
    An environment object holds the local variables of a scope
    and is chained through the lexical scope.
    """

    def __init__(self, parent=None):
        # The lexical parent
        self.parent = parent

        if parent is not None:
            self.vm = parent.vm
        else:
            self.vm = None

        # The values of local variables
        self.locals = []
        # The names of local variables
        self.locals_name = []
        # The mapping from name to index
        self.locals_map = {}

    def dup(self):
        """\
        Create a copy of self.
        """
        env = Environment(self.parent)
        env.locals = list(self.locals)
        env.locals_name = list(self.locals_name)
        env.locals_map = dict(self.locals_map)
        return env

    def assign_local(self, idx, value):
        """\
        Assign value to the local variable stored at idx.
        """
        self.locals[idx] = value

    def read_local(self, idx):
        """\
        Get the value of the local variable stored at idx.
        """
        return self.locals[idx]

    def alloc_local(self, name, value=Undef()):
        """\
        Allocate space for storing local variable. Return
        the index for the variable.

        Allocating a variable with the same name several times
        is OK. They will be stored at the same location, and
        value assigned later will overwrite earlier values.
        """
        idx = self.locals_map.get(name)
        if idx is not None:
            if value is not Undef():
                self.locals[idx] = value
            return idx
        idx = len(self.locals)
        self.locals_name.append(name)
        self.locals.append(value)
        self.locals_map[name] = idx
        return idx

    def find_local(self, name):
        """\
        Find the location(index) where the local variable is
        stored. Return None if no variable with given name is
        found.
        """
        return self.locals_map.get(name)

    def get_name(self, idx):
        """\
        Get the name of the local variable stored at the given
        location(index). Used in debugging.
        """
        return self.locals_name[idx]

    def lookup_location(self, name):
        """\
        Find the location of variable with given name. Recursively
        find in parent when necessary.
        """
        env = self
        while env is not None:
            idx = env.find_local(name)
            if idx is not None:
                return Location(env, idx)
            env = env.parent
        return None

    def __repr__(self):
        return "<Environment @%X>" % id(self)
