from skime.vm import VM
from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse

class HelperVM(object):
    def __init__(self):
        self.compiler = Compiler()
        
    def eval(self, code):
        vm = VM()
        proc = self.compiler.compile(parse(code), vm.ctx)
        return vm.run(proc)

