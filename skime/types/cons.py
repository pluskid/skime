class Cons(object):
    """\
    The Cons pair of Scheme.

    Cons can be chained to form a list. The Python value None acts as
    end-of-list.

      Cons(1, Cons(2, None)) <==> '(1 2) <==> '(1 . (2 . ()))
    """
    __slots__ = ['car', 'cdr']

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __eq__(self, other):
        return isinstance(other, Cons) and \
               self.car == other.car and \
               self.cdr == other.cdr
