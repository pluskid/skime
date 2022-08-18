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

    def get_car(self):
        return self.first
    def set_car(self, val):
        self.first = val
    def get_cdr(self):
        return self.rest
    def set_cdr(self, val):
        self.rest = val
    car = property(get_car, set_car)
    cdr = property(get_cdr, set_cdr)

    def __eq__(self, other):
        return isinstance(other, Pair) and \
               self.first == other.first and \
               self.rest == other.rest
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    def __str__(self):
        segments = [self.first.__str__()]
        elems = self.rest

        while isinstance(elems, Pair):
            segments.append(elems.first.__str__())
            elems = elems.rest

        if elems is not None:
            segments.append(".")
            segments.append(elems.__str__())
        return '(' + ' '.join(segments) + ')'
