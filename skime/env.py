class Environment(object):
    """\
    An environment object holds the local variables of a scope
    and is chained through the lexical scope.
    """

    def __init__(self, parent=None):
        # The lexical parent
        self.parent = parent

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

    def alloc_local(self, name, value=None):
        """\
        Allocate space for storing local variable. Return
        the index for the variable.

        Allocating a variable with the same name several times
        is OK. They will be stored at the same location, and
        value assigned later will overwrite earlier values.
        """
        idx = self.locals_map.get(name)
        if idx is not None:
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

