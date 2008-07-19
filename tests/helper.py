import sys
from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from skime.vm import VM
from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse

class HelperVM(object):
    def __init__(self):
        self.compiler = Compiler()
        
    def eval(self, code):
        vm = VM()
        proc = self.compiler.compile(parse(code), vm.env)
        return vm.run(proc)

