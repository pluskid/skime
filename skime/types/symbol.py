import weakref

class Symbol(object):
    symbols = weakref.WeakValueDictionary({})

    def __new__(cls, name):
        """\
        Get the interned symbol of name. If no found, create
        a new interned symbol.
        """
        if name in cls.symbols:
            return cls.symbols[name]

        sym = object.__new__(cls)
        sym._name = name
        cls.symbols[name] = sym
        return sym

    def __eq__(self, other):
        return self is other
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    def get_name(self):
        return self._name
    def set_name(self):
        raise AttributeError("Can't modify name of a symbol.")
    name = property(get_name, set_name)

    def __str__(self):
        return self.name
    def __repr__(self):
        return "<symbol %s>" % self._name.__repr__()
