import math

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

class PyCallable(Primitive):
    def __init__(self, proc):
        self.proc = proc

    def check_arity(self, argc):
        return True

    def call(self, vm, *args):
        return self.proc(*args)

def load_primitives(env):
    "Load primitives into an Environment."
    env.alloc_local('+', PyPrimitive(plus, (-1, -1)))
    env.alloc_local('-', PyPrimitive(minus, (1, -1)))
    env.alloc_local('*', PyPrimitive(mul, (-1, -1)))
    env.alloc_local('/', PyPrimitive(div, (1, -1)))
    env.alloc_local('=', PyPrimitive(equal, (-1, -1)))
    env.alloc_local('<', PyPrimitive(less, (2, -1)))
    env.alloc_local('>', PyPrimitive(more, (2, -1)))
    env.alloc_local('<=', PyPrimitive(less_equal, (2, -1)))
    env.alloc_local('>=', PyPrimitive(more_equal, (2, -1)))

    env.alloc_local('equal?', PyPrimitive(prim_equal, (2, 2)))
    env.alloc_local('eq?', PyPrimitive(prim_eqv, (2, 2)))
    env.alloc_local('eqv?', PyPrimitive(prim_eqv, (2, 2)))

    env.alloc_local("log", PyPrimitive(prim_log, (1, 1)))
    env.alloc_local("exp", PyPrimitive(prim_exp, (1, 1)))
    env.alloc_local("sin", PyPrimitive(prim_sin, (1, 1)))
    env.alloc_local("cos", PyPrimitive(prim_cos, (1, 1)))
    env.alloc_local("tan", PyPrimitive(prim_tan, (1, 1)))
    env.alloc_local("abs", PyPrimitive(prim_abs, (1, 1)))
    
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
                   ((int, int, float, complex), "number?"),
                   ((int, int, float), "rational?"),
                   ((int, int, float), "real?"),
                   ((int, int, float, complex), "complex?"),
                   ((int, int), "integer?"),
                   ((Procedure, Primitive), "procedure?")]:
        env.alloc_local(name, PyPrimitive(make_type_predict(t), (1, 1)))

    env.alloc_local('exact?', PyPrimitive(prim_exact_p, (1, 1)))
    env.alloc_local('inexact?', PyPrimitive(prim_inexact_p, (1, 1)))
    env.alloc_local('zero?', PyPrimitive(prim_zero_p, (1, 1)))
    env.alloc_local('positive?', PyPrimitive(prim_positive_p, (1, 1)))
    env.alloc_local('negative?', PyPrimitive(prim_negative_p, (1, 1)))
    env.alloc_local('even?', PyPrimitive(prim_even_p, (1, 1)))
    env.alloc_local('odd?', PyPrimitive(prim_odd_p, (1, 1)))
    env.alloc_local('max', PyPrimitive(prim_max, (1, -1)))
    env.alloc_local('min', PyPrimitive(prim_min, (1, -1)))
    env.alloc_local('quotient', PyPrimitive(prim_quotient, (2, 2)))
    env.alloc_local('modulo', PyPrimitive(prim_modulo, (2, 2)))
    env.alloc_local('remainder', PyPrimitive(prim_remainder, (2, 2)))
    env.alloc_local('gcd', PyPrimitive(prim_gcd, (-1, -1)))
    env.alloc_local('lcm', PyPrimitive(prim_lcm, (-1, -1)))
    env.alloc_local('floor', PyPrimitive(prim_floor, (1, 1)))
    env.alloc_local('ceiling', PyPrimitive(prim_ceiling, (1, 1)))
    env.alloc_local('truncate', PyPrimitive(prim_truncate, (1, 1)))
    env.alloc_local('round', PyPrimitive(prim_round, (1, 1)))
    env.alloc_local('asin', PyPrimitive(prim_asin, (1, 1)))
    env.alloc_local('acos', PyPrimitive(prim_acos, (1, 1)))
    env.alloc_local('atan', PyPrimitive(prim_atan, (1, 2)))
    env.alloc_local('sqrt', PyPrimitive(prim_sqrt, (1, 1)))
    env.alloc_local('expt', PyPrimitive(prim_expt, (2, 2)))
    env.alloc_local('null?', PyPrimitive(prim_null_p, (1, 1)))
    env.alloc_local('list?', PyPrimitive(prim_list_p, (1, 1)))

    env.alloc_local('apply', PyPrimitive(prim_apply, (1, -1)))
    env.alloc_local('map', PyPrimitive(prim_map, (2, -1)))

    env.alloc_local('string->symbol', PyPrimitive(prim_string_to_symbol, (1, 1)))
    env.alloc_local('symbol->string', PyPrimitive(prim_symbol_to_string, (1, 1)))
    env.alloc_local('number->string', PyPrimitive(prim_number_to_string, (1, 2)))
    env.alloc_local('string->number', PyPrimitive(prim_string_to_number, (1, 2)))
    env.alloc_local('string-append', PyPrimitive(prim_string_append, (-1, -1)))

def type_error_decorator(meth):
    "Decorate method to catch Python TypeError and raise skime WrongArgType"
    def new_meth(*args):
        try:
            return meth(*args)
        except TypeError as e:
            raise WrongArgType(*e.args)
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
        return 1.0/num
    if isinstance(num, int):
        num = float(num)
    for x in args:
        num /= x
    return num

def equal(vm, *args):
    if len(args) < 2:
        return True
    a = args[0]
    b = args[1]
    type_check(a, (int, int, float, complex))
    type_check(b, (int, int, float, complex))
    if a != b:
        return False
    for x in args[2:]:
        type_check(a, (int, int, float, complex))
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

def prim_positive_p(vm, arg):
    type_check(arg, (int, int, float))
    return arg > 0
def prim_negative_p(vm, arg):
    type_check(arg, (int, int, float))
    return arg < 0
def prim_odd_p(vm, arg):
    type_check(arg, (int, int))
    return arg % 2 != 0
def prim_even_p(vm, arg):
    type_check(arg, (int, int))
    return arg % 2 == 0
def prim_max(vm, *args):
    return max(args)
def prim_min(vm, *args):
    return min(args)
def prim_quotient(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    return a/b
# remainder has the same sign as b
def prim_remainder(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    if a > 0:
        return a%b
    return (-a)%(-b)
# modulo has the same sign as a
def prim_modulo(vm, a, b):
    type_check(a, (int, int))
    type_check(b, (int, int))
    return a%b


def gcd(a, b):
    while b != 0:
        b, a = a % b, b
    return a
def lcm(a, b):
    return a*b/gcd(a, b)
def prim_gcd(vm, *args):
    if args is None:
        return 0
    if len(args) == 1:
        return abs(args[0])
    a, b, args = args[0], args[1], args[2:]
    type_check(a, (int, int))
    type_check(b, (int, int))
    g = gcd(a, b)
    for x in args:
        type_check(x, (int, int))
        g = gcd(g, x)
    return abs(g)
    
def prim_lcm(vm, *args):
    if args is None:
        return 1
    if len(args) == 1:
        return abs(args[0])
    a, b, args = args[0], args[1], args[2:]
    type_check(a, (int, int))
    type_check(b, (int, int))
    l = lcm(a, b)
    for x in args:
        type_check(x, (int, int))
        l = lcm(l, x)
    return abs(l)

    
@type_error_decorator
def prim_floor(vm, a):
    return math.floor(a)
@type_error_decorator
def prim_ceiling(vm, a):
    return math.ceil(a)
@type_error_decorator
def prim_truncate(vm, a):
    if a > 0:
        return math.floor(a)
    return math.ceil(a)
@type_error_decorator
def prim_round(vm, a):
    return round(a)

@type_error_decorator
def prim_exp(vm, arg):
    return math.exp(arg)

@type_error_decorator
def prim_log(vm, arg):
    return math.log(arg)

@type_error_decorator
def prim_sin(vm, arg):
    return math.sin(arg)

@type_error_decorator
def prim_cos(vm, arg):
    return math.cos(arg)

@type_error_decorator
def prim_tan(vm, arg):
    return math.tan(arg)

@type_error_decorator
def prim_asin(vm, arg):
    return math.asin(arg)

@type_error_decorator
def prim_acos(vm, arg):
    return math.acos(arg)

@type_error_decorator
def prim_atan(vm, arg, *arg2):
    if arg2 is None:
        return math.atan(arg)
    else:
        return math.atan(float(arg2[0])/arg)

@type_error_decorator
def prim_sqrt(vm, arg):
    return math.sqrt(arg)

@type_error_decorator
def prim_expt(vm, a, b):
    return a ** b

@type_error_decorator
def prim_abs(vm, arg):
    return abs(arg)

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

def prim_exact_p(vm, arg):
    if isinstance(arg, int):
        return True
    # python complex are always inexact
    if isinstance(arg, (float, complex)):
        return False
    raise WrongArgType("Expecting a number, but got %s" % arg)
def prim_inexact_p(vm, arg):
    return not prim_exact_p(vm, arg)

def prim_zero_p(vm, arg):
    type_check(arg, (int, int, complex, float))
    return arg == 0
    
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

def prim_number_to_string(vm, num, radix=10):
    if radix == 10:
        return str(num)
    type_check(num, (int, int))
    minus = False
    if num < 0:
        minus = True
        num = -num
    
    if radix == 2:
        ditigs = []
        while num != 0:
            digits.append(num & 1)
            num = num >> 1
        num.reverse()
        fmt = ''.join(num)

    if radix == 8:
        fmt = '%o' % num
    if radix == 16:
        fmt = '%X' % num

    if minus:
        return '-' + fmt
    return fmt

def prim_string_to_number(vm, s, radix=10):
    try:
        return int(s, radix)
    except ValueError:
        if radix != 10:
            raise MiscError("Only radix 10 is permitted for decimal number")
        try:
            if s[-1] == 'i':
                # complex number
                return complex(s[:-1]+'j')
            else:
                return float(s)
        except ValueError:
            return False

@type_error_decorator
def prim_string_append(vm, *strings):
    return ''.join(strings)

def prim_equal(vm, a, b):
    return a == b

def prim_eqv(vm, a, b):
    return a is b


########################################
# Helper for primitives
########################################
def make_type_predict(tt):
    def predict(vm, obj):
        return isinstance(obj, tt)
    return predict

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
