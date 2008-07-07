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
from errors import SyntaxError

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
                  "Instruction %s expects %d parameters, but %d given" % \
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

        proc = Procedure(self.argc, self.fixed_argc, self.locals[:], self.literals[:], bc)

        return proc


class Compiler(object):
    sym_begin = sym("begin")
    sym_define = sym("define")
    sym_if = sym("if")
    sym_lambda = sym("lambda")
    
    def __init__(self):
        self.label_seed = 0

    def compile(self, lst, ctx):
        g = Generator(parent=ctx)
        
        if type(lst) is sym:
            g.emit_local("push", lst.name)
            g.emit("ret")
        elif type(lst) in [unicode, str, float, int, long, NoneType]:
            g.emit("push_literal", lst)
            g.emit("ret")
        elif type(lst) is cons:
            if lst.car == Compiler.sym_begin:
                self.generate_body(g, lst.cdr)
        else:
            raise CompileError("Cannot compile %s" % lst)

        return g.generate()

    ########################################
    # Helper functions
    ########################################
    def generate_body(self, g, body):
        "Generate scope body."
        if body is None:
            g.emit("push_nil")

        while body is not None:
            expr = body.car
            body = body.cdr
            self.generate_expr(g, expr, keep=body is None)

        g.emit("ret")

    def next_label(self):
        self.label_seed += 1
        return "__lbl_%d" % self.label_seed

    def generate_expr(self, g, expr, keep=True):
        """\
        Generate instructions for an expression.

        if keep == True, the value of the expression is kept on
        the stack, otherwise, it is popped or never pushed.
        """
        if type(expr) is sym:
            if keep:
                g.emit_local("push", expr.name)

        elif type(expr) in [unicode, str, float, int, long, NoneType, bool]:
            if keep:
                g.emit("push_literal", expr)

        elif type(expr) is cons:
            if expr.car == Compiler.sym_if:
                self.generate_if_expr(g, expr.cdr, keep=keep)

            elif expr.car == Compiler.sym_lambda:
                self.generate_lambda(g, expr.cdr, keep=keep)

            elif expr.car == Compiler.sym_define:
                self.generate_define(g, expr.cdr, keep=keep)
                
            else:
                argc = 0
                arg  = expr.cdr
                while arg is not None:
                    self.generate_expr(g, arg.car, keep=True)
                    arg = arg.cdr
                    argc += 1
                self.generate_expr(g, expr.car, keep=True)
                g.emit("call", argc)

        else:
            raise CompileError("Expecting atom or list, but got %s" % expr)

    def generate_if_expr(self, g, expr, keep=True):
        if expr is None:
            raise SyntaxError("Missing condition expression in 'if'")
            
        cond = expr.car
        expthen = expr.cdr
        if expthen is None:
            raise SyntaxError("Missing 'then' expression in 'if'")
        expthen = expthen.car
                
        expelse = expr.cdr.cdr
        if expelse is not None:
            if expelse.cdr is not None:
                raise SyntaxError("Extra expression in 'if'")
            expelse = expelse.car

            self.generate_expr(g, cond, keep=True)
                
            if keep is True:
                lbl_then = self.next_label()
                lbl_end = self.next_label()
                g.emit('goto_if_true', lbl_then)
                if expelse is None:
                    g.emit('push_nil')
                else:
                    self.generate_expr(g, expelse, keep=True)
                g.emit('goto', lbl_end)
                g.def_label(lbl_then)
                self.generate_expr(g, expthen, keep=True)
                g.def_label(lbl_end)
            else:
                if expelse is None:
                    lbl_end = self.next_label()
                    g.emit('goto_if_not_true', lbl_end)
                    self.generate_expr(g, expthen, keep=False)
                    g.def_label(lbl_end)
                else:
                    lbl_then = self.next_label()
                    lbl_end = self.next_label()
                    g.emit('goto_if_true', lbl_then)
                    self.generate_expr(g, expelse, keep=False)
                    g.emit('goto', lbl_end)
                    g.def_label(lbl_then)
                    self.generate_expr(g, expthen, keep=False)
                    g.def_label(lbl_end)
                    
    def generate_lambda(self, base_generator, expr, keep=True):
        if keep is not True:
            return  # lambda expression has no side-effect
        try:
            arglst = expr.car
            body = expr.cdr

            if type(arglst) is cons:
                args = []
                while type(arglst) is cons:
                    args.append(arglst.car.name)
                    arglst = arglst.cdr
                if arglst is None:
                    rest_arg = False
                else:
                    args.append(arglst.name)
                    rest_arg = True
            else:
                rest_arg = True
                args = [arglst.name]

            g = base_generator.push_proc(args=args, rest_arg=rest_arg)
            self.generate_body(g, body)
            base_generator.emit("make_lambda")

        except AttributeError:
            raise SyntaxError("Broken lambda expression")
        
    def generate_define(self, g, expr, keep=True):
        if expr is None:
            raise SyntaxError("Empty define expression")
        var = expr.car
        val = expr.cdr
        if type(var) is not sym:
            raise SyntaxError("The variable to define should be a symbol")
        if val is None:
            raise SyntaxError("Missing value for defined variable")
        if val.cdr is not None:
            raise SyntaxError("Extra expressions in 'define'")
        val = val.car

        self.generate_expr(g, val, keep=True)
        if keep is True:
            g.emit("dup")
        g.def_local(var.name)
        g.emit_local('set', var.name)
        
