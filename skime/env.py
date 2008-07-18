class Environment(object):
    """\
    An environment object holds the local variables of a scope
    and is chained through the lexical scope.
    """

    def __init__(self, parent):
        # The lexical parent
        self.parent = parent

        # The values of local variables
        self.locals = []
        # The names of local variables
        self.locals_name = []
        # The mapping from name to index
        self.locals_map = {}
        
    def alloc_local(self, name):
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
        self.locals.append(Environment.undef)
        self.locals_map[name] = idx
        return idx

    def find_local(self, name):
        """\
        Find the location(index) where the local variable is
        stored. KeyError will raise if no local variable with
        the given name is found.
        """
        return self.locals_map[name]

    def get_name(self, idx):
        """\
        Get the name of the local variable stored at the given
        location(index). Used in debugging.
        """
        return self.locals_name[idx]

