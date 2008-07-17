class Pair(object):
    """\
    The Pair pair of Scheme.

    Pair can be chained to form a list. The Python value None acts as
    end-of-list.

      Pair(1, Pair(2, None)) <==> '(1 2) <==> '(1 . (2 . ()))
    """
    __slots__ = ['first', 'rest']

    def __init__(self, first, rest):
        self.first = first
        self.rest = rest

    def __eq__(self, other):
        return isinstance(other, Pair) and \
               self.first == other.first and \
               self.rest == other.rest
