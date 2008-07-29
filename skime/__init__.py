from .compiler.parser import parse
from .compiler.compiler import Compiler
from .vm import VM as SkimeVM
from .types.symbol import Symbol
from .types.pair import Pair
from .prim import prim_list_p, iter_list

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

    eol = None
    def __init__(self, profile):
        # TODO: deal with profile
        self.vm = SkimeVM()
        self.compiler = Compiler()
    
    def compile(self, code):
        return self.compiler.compile(parse(code), self.vm.env)

    def eval(self, compiled):
        return self.vm.run(compiled)

    def repl(self):
        pass

    def get(self, name, default=None):
        idx = self.vm.env.find_local(name)
        if idx is not None:
            return self.vm.env.read_local(idx)
        else:
            return default

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
        
        mapping = {
            list: pylist_to_scmlist,
            dict: dict_to_scmalist
            }
        proc = mapping.get(type(val))
        if proc is not None:
            return proc(val, shallow)
        return val

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
                return lst
            return val

        return val

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
        return object
