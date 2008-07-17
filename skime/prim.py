from .types.symbol import Symbol as sym
from .types.pair   import Pair as pair
from .proc         import Procedure
from .errors       import WrongArgNumber
from .errors       import WrongArgType

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
    ctx.add_local('=', PyPrimitive(equal, (2, -1)))

    ctx.add_local('first', PyPrimitive(prim_first, (1, 1)))
    ctx.add_local('rest', PyPrimitive(prim_rest, (1, 1)))
    ctx.add_local('pair', PyPrimitive(prim_pair, (2, 2)))
    ctx.add_local('car', PyPrimitive(prim_first, (1, 1)))
    ctx.add_local('cdr', PyPrimitive(prim_rest, (1, 1)))
    ctx.add_local('cons', PyPrimitive(prim_pair, (2, 2)))

    for t,name in [(bool, "boolean?"),
                   (pair, "pair?"),
                   (sym, "symbol?"),
                   (str, "string?"),
                   ((int, long, float, complex), "number?"),
                   ((Procedure, Primitive), "procedure?")]:
        ctx.add_local(name, PyPrimitive(make_type_predict(t), (1, 1)))


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
def equal(a, b, *args):
    if a != b:
        return False
    for x in args:
        if x != a:
            return False
    return True

def prim_first(arg):
    type_check(arg, pair)
    return arg.first
def prim_rest(arg):
    type_check(arg, pair)
    return arg.rest
def prim_pair(a, b):
    return pair(a, b)


########################################
# Helper for primitives
########################################
def make_type_predict(types):
    def predict_single(obj):
        return isinstance(obj, types[0])
    def predict_many(obj):
        for t in types:
            if isinstance(obj, t):
                return True
        return False
    if isinstance(types, tuple):
        return predict_many
    return predict_single

def type_check(obj, t):
    if not isinstance(obj, t):
        raise WrongArgType("Expecting type %s, but got %s (type %s)" % \
                           (t, obj, type(obj)))

