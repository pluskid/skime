from array  import array

from ..iset import INSN_MAP
from ..proc import Procedure

class Generator(object):
    """\
    A Generator provide an easy way to genetate bytecode.
    """

    def __init__(self, parent=None, args=[], rest_arg=False):
        """\
        Create a generator for a procedure.

          - parent: A duck typing parent acting as a lexical context parent.
          - args: a list of arguments for the procedure
          - rest_arg: if True, the last one of args is a 'rest argument'. e.g.
                      (lambda (a b . c) ...) =>
                          args = ['a', 'b', 'c'], rest_arg = True
        """
        self.stream = []
        self.labels = {}
        self.literals = []
        self.locals = args[:]

        self.argc = len(args)
        if rest_arg:
            self.fixed_argc = self.argc-1
        else:
            self.fixed_argc = self.argc
        self.ip = 0
        self.parent = parent

    def emit(self, insn_name, *args):
        "Emit an instruction"
        insn = INSN_MAP.get(insn_name)
        if insn is None:
            raise TypeError, "No such instruction: %s" % insn_name
        if insn.length != 1+len(args):
            raise TypeError, \
                  "INSTRUCTION %s expects %d parameters, but %d given" % \
                  (insn_name, insn.length-1, len(args))
        self.stream.append((insn_name, args))
        self.ip += len(args)+1

    def def_local(self, *locals):
        "Define local variables."
        for loc in locals:
            if loc in self.locals:
                raise TypeError, "Duplicated local variable: %s" % loc
        self.locals += locals

    def def_label(self, name):
        "Define a label at current ip."
        if self.labels.get(name) is not None:
            raise TypeError, "Duplicated label: %s" % name
        self.labels[name] = self.ip

    def push_proc(self, args=[], rest_arg=False):
        """\
        Return a generator g for generating a procedure in the context. Use
        g to generate the body of the procedure.

        Later when self.generate is called, g.generate will be called
        automatically to get the procedure object, add it to the literals
        and push to the operand stack.
        """
        g = Generator(parent=self, args=args, rest_arg=rest_arg)
        # generate_proc is a pseudo instruction
        self.stream.append(('generate_proc', g))
        
        return g

    def emit_local(self, action, name):
        """\
        Emit an instruction to push or set local variable. The local variable
        is automatically searched in the current context and parents.
        """
        depth, idx = self.find_local_depth(name)
        if depth < 0:
            raise UnboundVariable(name, "Unbound variable %s" % name)
        if depth == 0:
            postfix = ''
            args = (idx,)
        else:
            postfix = '_depth'
            args = (depth, idx)
        self.emit('%s_local%s' % (action, postfix), *args)

    def find_local(self, name):
        "Find index of a local variable in the current context."
        return self.locals.index(name)

    def find_local_depth(self, name):
        """\
        Find depth and index of a local variable. Recursively find in parents.
        Return a depth of -1 when not found.
        """
        depth = 0
        ctx = self
        while ctx is not None:
            try:
                return (depth, ctx.find_local(name))
            except ValueError:
                depth += 1
                ctx = ctx.parent
        return (-1, 0)
    
    def generate(self):
        "Generate a Procedure based on the knowledge collected."
        bc = array('i')
        for insn_name, args in self.stream:
            # pseudo instructions
            if insn_name == 'generate_proc':
                idx = len(self.literals)
                self.literals.append(args.generate())
                bc.append(INSN_MAP['push_literal'].opcode)
                bc.append(idx)
            # real instructions
            else:
                insn = INSN_MAP[insn_name]
                bc.append(insn.opcode)

                if insn_name in ['goto', 'goto_if_true', 'goto_if_not_true']:
                    bc.append(self.labels[args[0]])
                elif insn_name == 'push_literal':
                    idx = len(self.literals)
                    self.literals.append(args[0])
                    bc.append(idx)
                else:
                    for x in args:
                        bc.append(x)

        proc = Procedure(self.argc, self.fixed_argc,
                         self.locals[:], self.literals[:], bc)

        return proc
