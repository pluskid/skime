from types          import NoneType
                      
from ..types.symbol import Symbol as sym
from ..types.cons   import Cons as cons
                     
from ..errors       import CompileError
from ..errors       import SyntaxError

from .generator     import Generator

class Compiler(object):
    """\
    The compiler for skime. It compiles sexp to bytecode.
    """

    sym_begin = sym("begin")
    sym_define = sym("define")
    sym_set_x = sym("set!")
    sym_if = sym("if")
    sym_lambda = sym("lambda")
    
    def __init__(self):
        self.label_seed = 0

    def compile(self, lst, ctx):
        g = Generator(parent=ctx)

        self.generate_expr(g, lst, keep=True)

        proc = g.generate()
        proc.lexical_parent = ctx
        return proc

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
        mapping = {
            Compiler.sym_if: self.generate_if_expr,
            Compiler.sym_begin: self.generate_begin_expr,
            Compiler.sym_lambda: self.generate_lambda,
            Compiler.sym_define: self.generate_define,
            Compiler.sym_set_x: self.generate_set_x
            }
        
        if type(expr) is sym:
            if keep:
                g.emit_local("push", expr.name)

        elif type(expr) in [unicode, str, float, int, long, NoneType, bool]:
            if keep:
                g.emit("push_literal", expr)

        elif type(expr) is cons:
            routine = mapping.get(expr.car)
            if routine is not None:
                routine(g, expr.cdr, keep=keep)
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

    def generate_begin_expr(self, g, body, keep=True):
        "(begin ...) is transformed to ((lambda () ...))"
        gsub = g.push_proc(args=[], rest_arg=False)
        self.generate_body(gsub, body)
        g.emit("make_lambda")
        g.emit("call", 0)
        if not keep:
            g.emit("pop")

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
            elif arglst is None:
                rest_arg = False
                args = []
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
        
        if type(var) is cons:
            gen = self.generate_lambda
            val = cons(var.cdr, expr.cdr)
            var = var.car
        elif type(var) is sym:
            gen = self.generate_expr
            val = expr.cdr
            if val is None:
                raise SyntaxError("Missing value for defined variable")
            if val.cdr is not None:
                raise SyntaxError("Extra expressions in 'define'")
            val = val.car
        else:
            raise SyntaxError("Invalid define expression")

        # first define local, then generate value. This allow
        # recursive function to be compiled properly.
        g.def_local(var.name)
        gen(g, val, keep=True)
        if keep is True:
            g.emit("dup")
        g.emit_local('set', var.name)

    def generate_set_x(self, g, expr, keep=True):
        if expr is None:
            raise SyntaxError("Empty set! expression")
        var = expr.car

        if not isinstance(var, sym):
            raise SyntaxError("Invalid set! expression, expecting symbol")
        val = expr.cdr

        if val is None:
            raise SyntaxError("Missing value for set! expression")
        if val.cdr is not None:
            raise SyntaxError("Extra expressions in 'set!'")
        val = val.car

        self.generate_expr(g, val, keep=True)
        if keep:
            g.emit("dup")
        g.emit_local('set', var.name)
