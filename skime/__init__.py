from .compiler.parser import parse
from .compiler.compiler import Compiler
from .vm import VM as SkimeVM

class VM(object):
    "The compatibile wrapper layer to Schemepy."

    direct_types = {
        int: int,
        long: long,
        float: float,
        complex: complex,
        str: str
        }
    
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
        return val

    def fromscheme(self, val, shallow=False):
        return val

    def type(self, val):
        t = direct_types.get(type(val))
        if t is not None:
            return t
        return object
