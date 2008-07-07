"""\
The compiler for skime. It compiles sexp to bytecode.
"""

from array import array
from types import NoneType

from symbol import Symbol as sym
from cons import Cons as cons
from iset import INSN_MAP
from proc import Procedure

from errors import UnboundVariable
from errors import CompileError

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

        self.argc = len(args)
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

    def push_proc(self, args=[]):
        """\
        Return a generator g for generating a procedure in the context. Use
        g to generate the body of the procedure.

        Later when self.generate is called, g.generate will be called
        automatically to get the procedure object, add it to the literals
        and push to the operand stack.
        """
        g = Generator(parent=self, args=args)
        # generate_proc is a pseudo instruction
        self.stream.append(('generate_proc', g))
        
        return g

    def find_local(self, name):
        return self.locals.index(name)
    
    def generate(self):
        "Generate a Procedure based on the knowledge collected."
        proc = Procedure()
        
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
                elif insn_name in ['push_local', 'set_local']:
                    bc.append(self.find_local(args[0]))
#                 elif insn_name in ['push_local_depth', 'set_local_depth']:
#                     bc.append(args[0])
#                     p = self
#                     i = args[0]
#                     while i > 0:
#                         p = p.parent
#                         i -= 1
#                     bc.append(p.find_local(args[1]))
                else:
                    for x in args:
                        bc.append(x)
                
        proc.bytecode = bc
        proc.literals = self.literals[:]
        proc.locals = self.locals
        proc.argc = self.argc

        return proc


class Compiler(object):
    sym_begin = sym("begin")
    sym_define = sym("define")
    
    def __init__(self):
        pass

    def compile(self, lst, ctx):
        if type(lst) is sym:
            depth, idx = lookup_variable(ctx, lst.name)
            if depth < 0:
                raise UnboundVariable(lst.name, "Unbound variable %s" % lst.name)

            g = Generator(parent=ctx)
            g.emit("push_local_depth", depth+1, idx)
            g.emit("ret")
        elif type(lst) in [unicode, str, float, int, long, NoneType]:
            g = Generator(parent=ctx)
            g.emit("push_literal", lst)
            g.emit("ret")
        elif type(lst) is cons:
            if lst.car == Compiler.sym_begin:
                g = Generator(parent=ctx)
                self.generate_body(ctx, g, lst.cdr)
        else:
            raise CompileError("Cannot compile %s" % lst)

        return g.generate()

    ########################################
    # Helper functions
    ########################################
    def lookup_variable(self, ctx, name):
        "Lookup variables in lexical scope"
        depth = 0
        while ctx is not None:
            try:
                return (depth, ctx.find_local(name))
            except ValueError:
                depth += 1
                ctx = ctx.parent
        return (-1, 0)
        
    def generate_body(self, ctx, g, body):
        "Generate scope body."
        if body is None:
            g.emit("push_nil")

        while body is not None:
            expr = body.car
            body = body.cdr
            self.generate_expr(ctx, g, expr, keep=body is None)

        g.emit("ret")

    def generate_expr(self, ctx, g, expr, keep=True):
        """\
        Generate instructions for an expression.

        if keep == True, the value of the expression is kept on
        the stack, otherwise, it is popped or never pushed.
        """
        if type(expr) is sym:
            if keep:
                depth, idx = self.lookup_variable(g, expr.name)
                if depth < 0:
                    raise UnboundVariable(expr.name, "Unbound variable %s" % expr.name)
                if depth == 0:
                    g.emit("push_local", idx)
                else:
                    g.emit("push_local_depth", depth, idx)

        elif type(expr) in [unicode, str, float, int, long, NoneType]:
            if keep:
                g.emit("push_literal", expr)

        elif type(expr) is cons:
            if expr.car == Compiler.sym_define:
                name = expr.cdr.car
                g.def_local(name.name)
                value = expr.cdr.cdr.car
                self.generate_expr(ctx, g, expr, keep=True)
                if keep:
                    g.emit("dup")
                g.emit("set_local", name.name)
            else:
                argc = 0
                arg  = expr.cdr
                while arg is not None:
                    self.generate_expr(ctx, g, arg.car, keep=True)
                    arg = arg.cdr
                    argc += 1
                self.generate_expr(ctx, g, expr.car, keep=True)
                g.emit("call", argc)

        else:
            raise CompileError("Expecting atom or list, but got %s" % expr)

