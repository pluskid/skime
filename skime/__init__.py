from .compiler.parser import parse
from .compiler.compiler import Compiler
from .vm import VM as SkimeVM
from .types.symbol import Symbol
from .types.pair import Pair
from .prim import Primitive, PyCallable, prim_list_p, iter_list
from .proc import Procedure

import errors
from schemepy.exceptions import *
from schemepy.lam import Lambda

def dummy():
    pass
FunctionType = type(dummy)

class PyObj(object):
    def __init__(self, obj):
        self.obj = obj

class VM(object):
    "The compatibile wrapper layer to Schemepy."

    direct_types = {
        int: int,
        long: long,
        float: float,
        complex: complex,
        str: str,
        unicode: unicode,
        bool: bool,
        Symbol: Symbol
        }

    def __init__(self, profile):
        # TODO: deal with profile
        self.vm = SkimeVM()
        self.compiler = Compiler()

    def map_exception_deco(meth):
        mapping = {
            errors.UnboundVariable: ScmUnboundVariable,
            errors.WrongArgNumber: ScmWrongArgNumber,
            errors.WrongArgType: ScmWrongArgType,
            errors.SyntaxError: ScmSyntaxError,
            errors.ParseError: ScmSyntaxError,
            errors.MiscError: ScmMiscError
            }
        def new_meth(self, *args, **kw):
            try:
                return meth(self, *args, **kw)
            except Exception, e:
                t = mapping.get(type(e))
                if t is None:
                    t = ScmMiscError
                raise t(e.message)
        return new_meth

    @map_exception_deco
    def compile(self, code):
        return self.compiler.compile(parse(code), self.vm.env)

    @map_exception_deco
    def eval(self, compiled):
        return self.vm.run(compiled)

    def repl(self):
        pass

    def define(self, name, value):
        if isinstance(name, Symbol):
            name = name.name
        self.vm.env.alloc_local(name, value)
        
    def get(self, name, default=None):
        idx = self.vm.env.find_local(name)
        if idx is not None:
            return self.vm.env.read_local(idx)
        else:
            return default

    @map_exception_deco
    def apply(self, proc, args):
        return self.vm.apply(proc, args)

    def toscheme(self, val, shallow=False):
        def pylist_to_scmlist(lst, shallow):
            rest = None
            for x in reversed(lst):
                if shallow:
                    rest = Pair(x, rest)
                else:
                    rest = Pair(self.toscheme(x), rest)
            return rest
        def dict_to_scmalist(dic, shallow):
            lst = None
            for it in dic.iteritems():
                k, v = it
                key = self.toscheme(k)
                if shallow:
                    value = v
                else:
                    value = self.toscheme(v)
                lst = Pair(Pair(key, value), lst)
            return lst
        def pair_to_pair(p, shallow):
            if shallow:
                return Pair(p.first, p.rest)
            else:
                return Pair(self.toscheme(p.first),
                            self.toscheme(p.rest))
        
        mapping = {
            list: pylist_to_scmlist,
            dict: dict_to_scmalist,
            Pair: pair_to_pair
            }
        proc = mapping.get(type(val))
        if proc is not None:
            return proc(val, shallow)

        if isinstance(val, Lambda):
            return val._lambda

        if callable(val):
            return PyCallable(val)

        if VM.direct_types.has_key(type(val)):
            return val
        
        return PyObj(val)

    def fromscheme(self, val, shallow=False):
        if isinstance(val, Pair):
            if prim_list_p(self.vm, val):
                lst = []
                is_dict = True
                for item in iter_list(val):
                    lst.append(item)
                    if not isinstance(item, Pair):
                        is_dict = False
                if is_dict:
                    d = dict()
                    for x in lst:
                        k = self.fromscheme(x.first)
                        if shallow:
                            v = x.rest
                        else:
                            v = self.fromscheme(x.rest)
                        d[k] = v
                    return d
                else:
                    if shallow:
                        return lst
                    return [self.fromscheme(x) for x in lst]
            if shallow:
                return Pair(val.first, val.rest)
            else:
                return Pair(self.fromscheme(val.first),
                            self.fromscheme(val.rest))
        if val is None:
            return []

        if isinstance(val, PyCallable):
            return val.proc

        if isinstance(val, Primitive) or \
           isinstance(val, Procedure):
            return Lambda(val, self, shallow)

        if VM.direct_types.has_key(type(val)):
            return val

        if isinstance(val, PyObj):
            return val.obj

        raise ConversionError(val, "Don't know how to convert this type.")

    def type(self, val):
        t = VM.direct_types.get(type(val))
        if t is not None:
            return t
        if isinstance(val, Pair):
            if prim_list_p(self.vm, val):
                for item in iter_list(val):
                    if not isinstance(item, Pair):
                        return list
                return dict
            return Pair
        if val is None:
            return list
        if isinstance(val, PyCallable):
            return FunctionType
        if isinstance(val, Procedure) or \
           isinstance(val, Primitive):
            return Lambda
        if isinstance(val, PyObj):
            return object
        return type(None)
