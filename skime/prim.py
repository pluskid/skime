from .types.symbol import Symbol as sym
from .types.pair   import Pair as pair
from .proc         import Procedure
from .errors       import WrongArgNumber
from .errors       import WrongArgType
from .errors       import MiscError

class Primitive(object):
    """\
    Base class for all skime primitives.

    When primitive is called with arguments (1, 2, 3), the arity is first checked
    by calling prim.check_arity(3). Then the vm object is inserted as the first
    argument and the primitive called: prim.call(vm, 1, 2, 3). The vm is always
    the first argument of all primitives, but not count as argc.
    """
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


def load_primitives(env):
    "Load primitives into an Environment."
    env.alloc_local('+', PyPrimitive(plus, (-1, -1)))
    env.alloc_local('-', PyPrimitive(minus, (1, -1)))
    env.alloc_local('*', PyPrimitive(mul, (-1, -1)))
    env.alloc_local('/', PyPrimitive(div, (1, -1)))
    env.alloc_local('=', PyPrimitive(equal, (2, -1)))
    env.alloc_local('<', PyPrimitive(less, (2, -1)))
    env.alloc_local('>', PyPrimitive(more, (2, -1)))
    env.alloc_local('<=', PyPrimitive(less_equal, (2, -1)))
    env.alloc_local('>=', PyPrimitive(more_equal, (2, -1)))
                
    env.alloc_local('not', PyPrimitive(prim_not, (1, 1)))
        
    env.alloc_local('first', PyPrimitive(prim_first, (1, 1)))
    env.alloc_local('rest', PyPrimitive(prim_rest, (1, 1)))
    env.alloc_local('pair', PyPrimitive(prim_pair, (2, 2)))
    env.alloc_local('car', PyPrimitive(prim_first, (1, 1)))
    env.alloc_local('cdr', PyPrimitive(prim_rest, (1, 1)))
    env.alloc_local('cons', PyPrimitive(prim_pair, (2, 2)))
    env.alloc_local('set-first!', PyPrimitive(prim_set_first_x, (2, 2)))
    env.alloc_local('set-car!', PyPrimitive(prim_set_first_x, (2, 2)))
    env.alloc_local('set-rest!', PyPrimitive(prim_set_rest_x, (2, 2)))
    env.alloc_local('set-cdr!', PyPrimitive(prim_set_rest_x, (2, 2)))
    

    env.alloc_local('list', PyPrimitive(prim_list, (-1, -1)))

    for t,name in [(bool, "boolean?"),
                   (pair, "pair?"),
                   (sym, "symbol?"),
                   (str, "string?"),
                   ((int, long, float, complex), "number?"),
                   ((Procedure, Primitive), "procedure?")]:
        env.alloc_local(name, PyPrimitive(make_type_predict(t), (1, 1)))
    env.alloc_local('null?', PyPrimitive(prim_null_p, (1, 1)))
    env.alloc_local('list?', PyPrimitive(prim_list_p, (1, 1)))

    env.alloc_local('apply', PyPrimitive(prim_apply, (1, -1)))
    env.alloc_local('map', PyPrimitive(prim_map, (2, -1)))

    env.alloc_local('string->symbol', PyPrimitive(prim_string_to_symbol, (1, 1)))
    env.alloc_local('symbol->string', PyPrimitive(prim_symbol_to_string, (1, 1)))


def type_error_decorator(meth):
    "Decorate method to catch Python TypeError and raise skime WrongArgType"
    def new_meth(*args):
        try:
            return meth(*args)
        except TypeError, e:
            raise WrongArgType(e.message)
    return new_meth

@type_error_decorator
def plus(vm, *args):
    return sum(args)

@type_error_decorator
def mul(vm, *args):
    res = 1
    for x in args:
        res *= x
    return res

@type_error_decorator
def minus(vm, num, *args):
    if len(args) == 0:
        return -num
    for x in args:
        num -= x
    return num

@type_error_decorator
def div(vm, num, *args):
    if len(args) == 0:
        return 1/num
    for x in args:
        num /= x
    return num

def equal(vm, a, b, *args):
    if a != b:
        return False
    for x in args:
        if x != a:
            return False
    return True

def less(vm, a, b, *args):
    if a >= b:
        return False
    for x in args:
        if b >= x:
            return False
        b = x
    return True

def more(vm, a, b, *args):
    if a <= b:
        return False
    for x in args:
        if b <= x:
            return False
        b = x
    return True

def less_equal(vm, a, b, *args):
    if a > b:
        return False
    for x in args:
        if b > x:
            return False
        b = x
    return True

def more_equal(vm, a, b, *args):
    if a < b:
        return False
    for x in args:
        if b < x:
            return False
        b = x
    return True

def prim_not(vm, arg):
    if arg is False:
        return True
    return False

def prim_first(vm, arg):
    type_check(arg, pair)
    return arg.first
def prim_rest(vm, arg):
    type_check(arg, pair)
    return arg.rest
def prim_pair(vm, a, b):
    return pair(a, b)
def prim_set_first_x(vm, arg, val):
    type_check(arg, pair)
    arg.first = val
def prim_set_rest_x(vm, arg, val):
    type_check(arg, pair)
    arg.rest = val


def prim_null_p(vm, arg):
    return arg is None

# list?, detect circular list
def prim_list_p(vm, val):
    obj1 = val
    obj2 = val
    while True:
        if obj1 is None:
            return True
        if not isinstance(obj1, pair):
            return False

        obj1 = obj1.rest
        if obj1 is None:
            return True
        if not isinstance(obj1, pair):
            return False

        obj1 = obj1.rest
        obj2 = obj2.rest

        # circular
        if obj1 is obj2:
            break
        
    return False

def prim_list(vm, *args):
    lst = None
    for x in reversed(args):
        lst = pair(x, lst)
    return lst


def prim_apply(vm, proc, *args):
    if len(args) == 0:
        return vm.apply(proc, args)
    argv = list(args[:-1])
    arglst = args[-1]
    while isinstance(arglst, pair):
        argv.append(arglst.first)
        arglst = arglst.rest
    if arglst is not None:
        raise WrongArgType("The last argument of apply should be a valid list, but got %s" % args[-1])
    return vm.apply(proc, argv)

def prim_map(vm, proc, *lists):
    res = []
    while True:
        args = []
        end = False
        lists = list(lists)
        for i in range(len(lists)):
            lst = lists[i]
            if not isinstance(lst, pair):
                if lst is None:
                    end = True
                else:
                    raise WrongArgType("Arguments of map should be valid lists.")
            else:
                if end:
                    raise MiscError("Lists supplied to map should be all of the same length.")
                args.append(lst.first)
                lists[i] = lst.rest
        if end:
            break
        res.append(vm.apply(proc, args))
    rest = None
    for x in reversed(res):
        rest = pair(x, rest)
    return rest

def prim_string_to_symbol(vm, name):
    type_check(name, str)
    return sym(name)
def prim_symbol_to_string(vm, s):
    type_check(s, sym)
    return s.name


########################################
# Helper for primitives
########################################
def make_type_predict(tt):
    def predict_single(vm, obj):
        return isinstance(obj, tt)
    def predict_many(vm, obj):
        for t in tt:
            if isinstance(obj, t):
                return True
        return False
    if isinstance(tt, tuple):
        return predict_many
    return predict_single

def type_check(obj, t):
    if not isinstance(obj, t):
        raise WrongArgType("Expecting type %s, but got %s (type %s)" % \
                           (t, obj, type(obj)))

def iter_list(lst, excp_t=WrongArgType):
    while isinstance(lst, pair):
        yield lst.first
        lst = lst.rest
    if lst is not None:
        raise excp_t("Not a proper list")
