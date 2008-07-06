"""\
The compiler for skime. It compiles sexp to bytecode.
"""

from array import array
from symbol import Symbol as sym
from cons import Cons as cons
from iset import INSN_MAP
from proc import Procedure

class Generator(object):
    """\
    A Generator provide an easy way to genetate bytecode.
    """

    def __init__(self, parent=None, args=[]):
        """\
        Create a generator for a procedure.

          - args: a list of arguments for the procedure
        """
        self.stream = []
        self.labels = {}
        self.literals = []
        self.locals = args[:]
        self.ip = 0

        self.parent = parent

    def emit(self, insn_name, *args):
        "Emit an instruction"
        insn = INSN_MAP.get(insn_name)
        if insn is None:
            raise TypeError, "No such instruction: %s" % insn_name
        if insn.length != 1+len(args):
            raise TypeError, \
                  "Instruction %s expects %d parameters, but %d given" % \
                  (insn_name, insn.length-1, len(args))
        self._emit(insn_name, *args)

    def _emit(self, insn_name, *args):
        "Emit an instruction without validation. Internal use only."
        self.stream.append((insn_name, args))
        self.ip += len(args)+1

    def def_local(self, *locals):
        "Define local variables."
        for loc in locals:
            if loc in self.locals:
                raise TypeError, "Duplicated local variable: %s" % loc
        self._def_local(*locals)
    
    def _def_local(self, *locals):
        "Define local without validation. Internal use only."
        self.locals += locals

    def def_label(self, name):
        "Define a label at current ip."
        if self.labels.get(name) is not None:
            raise TypeError, "Duplicated label: %s" % name
        self._def_label(name)

    def _def_label(self, name):
        "Define a label at current ip without validation. Internal use only."
        self.labels[name] = self.ip
    
    def generate(self):
        "Generate a Procedure based on the knowledge collected."
        proc = Procedure()
        
        bc = array('i')
        for insn_name, args in self.stream:
            insn = INSN_MAP[insn_name]
            bc.append(insn.opcode)

            if insn_name in ['goto', 'goto_if_true', 'goto_if_not_true']:
                bc.append(self.labels[args[0]])
            elif insn_name == 'push_literal':
                idx = len(self.literals)
                self.literals.append(args[0])
                bc.append(idx)
            elif insn_name in ['push_local', 'set_local']:
                bc.append(self.locals.index(args[0]))
            elif insn_name in ['push_local_depth', 'set_local_depth']:
                bc.append(args[0])
                p = self
                i = args[0]
                while i > 0:
                    p = p.parent
                    i -= 1
                bc.append(p.locals.index(args[1]))
            else:
                for x in args:
                    bc.append(x)
                
        proc.bytecode = bc
        proc.literals = self.literals[:]
        proc.locals = self.locals

        return proc
