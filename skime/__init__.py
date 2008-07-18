from .compiler.parser import parse
from .compiler.compiler import Compiler
from .vm import VM as SkimeVM

class VM(object):
    "The compatibile wrapper layer to Schemepy."
    def __init__(self, profile):
        # TODO: deal with profile
        self.vm = SkimeVM()
        self.compiler = Compiler()
    
    def compile(self, code):
        return self.compiler.compile(parse(code), self.vm.ctx)

    def eval(self, compiled):
        return self.vm.run(compiled)

    def repl(self):
        pass

    def get(self, name, default=None):
        try:
            idx = self.vm.ctx.find_local(name)
            return self.vm.ctx.locals[idx]
        except ValueError:
            return default

    def apply(self, proc, args):
        return self.vm.run(proc, args)

    def toscheme(self, val, shallow=False):
        return val

    def fromscheme(self, val, shallow=False):
        return val
        
