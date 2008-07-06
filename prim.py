from symbol import Symbol as sym
from cons import Cons as cons
from errors import WrongArgNumber

class Primitive(object):
    "Base class for all skime primitives"
    def check_arity(self, argc):
        "Check whether this primitive is OK to execute with argc arguments."
        raise TypeError("check_arity is not implemented in abstract class Primitive")

    def call(self, *args):
        "Call the primitive with args."
        raise TypeError("call is not implemented in abstract class Primitive")


class PyPrimitive(Primitive):
    "Primitive wrapping a Python callable."
    def __init__(self, proc, arity):
        """\
        Create a PyPrimitive.

          proc  should be a Python callable.
          arity can be a tuple specifying the min and max number of arguments.
                either min or max or both can be -1, which means it is of no
                bound.
        """
        self.proc = proc
        self.arity = arity
        
    def check_arity(self, argc):
        min, max = self.arity
        if min > 0 and argc < min:
            raise WrongArgNumber("%s expects at least %d arguments, but got %d",
                                 (self.proc.__name__, min, argc))
        if max > 0 and argc > max:
            raise WrongArgNumber("%s expects at most %d arguments, but got %d",
                                 (self.proc.__name__, max, argc))

    def call(self, *args):
        return self.proc(*args)

    def __str__(self):
        return "<skime primitive => %s>" % self.proc.__name__


def load_primitives(ctx):
    "Load primitives into a top-level context."
    ctx.add_local('+', PyPrimitive(plus, (-1, -1)))
    ctx.add_local('-', PyPrimitive(minus, (1, -1)))
    ctx.add_local('*', PyPrimitive(mul, (-1, -1)))
    ctx.add_local('/', PyPrimitive(div, (1, -1)))


def plus(*args):
    return sum(args)
def mul(*args):
    res = 1
    for x in args:
        res *= x
    return res
def minus(num, *args):
    if len(args) == 0:
        return -num
    for x in args:
        num -= x
    return num
def div(num, *args):
    if len(args) == 0:
        return 1/num
    for x in args:
        num /= x
    return num

