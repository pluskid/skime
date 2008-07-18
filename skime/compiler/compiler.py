from types          import NoneType
                      
from ..types.symbol import Symbol as sym
from ..types.pair   import Pair as pair
                     
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
    sym_quote = sym("quote")
    
    def __init__(self):
        self.label_seed = 0

    def compile(self, lst, ctx):
        g = Generator(parent=ctx)

        self.generate_expr(g, lst, keep=True, tail=True)

        proc = g.generate()
        proc.lexical_parent = ctx
        return proc

    ########################################
    # Helper functions
    ########################################
    def self_evaluating(self, expr):
        for t in [int, long, complex, float, str, unicode, bool, NoneType]:
            if isinstance(expr, t):
                return True
        return False
        
    def next_label(self):
        self.label_seed += 1
        return "__lbl_%d" % self.label_seed

    def generate_body(self, g, body, keep=True, tail=False):
        "Generate scope body."
        if body is None and keep:
            g.emit("push_nil")

        while body is not None:
            expr = body.first
            body = body.rest
            will_keep = keep and body is None
            self.generate_expr(g, expr, keep=will_keep, tail=will_keep and tail)

    def generate_expr(self, g, expr, keep=True, tail=False):
        """\
        Generate instructions for an expression.

        if keep == True, the value of the expression is kept on
        the stack, otherwise, it is popped or never pushed.

        if tail == True, a tail call or ret will be emitted. tail
        can never be true if keep is False.
        """
        mapping = {
            Compiler.sym_if: self.generate_if_expr,
            Compiler.sym_begin: self.generate_body,
            Compiler.sym_lambda: self.generate_lambda,
            Compiler.sym_define: self.generate_define,
            Compiler.sym_set_x: self.generate_set_x,
            Compiler.sym_quote: self.generate_quote,
            }
        if self.self_evaluating(expr):
            if keep:
                g.emit('push_literal', expr)
                if tail:
                    g.emit('ret')
        
        elif isinstance(expr, sym):
            if keep:
                g.emit_local("push", expr.name)
                if tail:
                    g.emit('ret')

        elif isinstance(expr, pair):
            routine = mapping.get(expr.first)
            if routine is not None:
                routine(g, expr.rest, keep=keep, tail=tail)
            else:
                argc = 0
                arg  = expr.rest
                while arg is not None:
                    self.generate_expr(g, arg.first, keep=True, tail=False)
                    arg = arg.rest
                    argc += 1
                self.generate_expr(g, expr.first, keep=True, tail=False)
                if tail:
                    g.emit('tail_call', argc)
                else:
                    g.emit('call', argc)
                    if not keep:
                        g.emit('pop')

        else:
            raise CompileError("Expecting atom or list, but got %s" % expr)

    def generate_if_expr(self, g, expr, keep=True, tail=False):
        if expr is None:
            raise SyntaxError("Missing condition expression in 'if'")
            
        cond = expr.first
        expthen = expr.rest
        if expthen is None:
            raise SyntaxError("Missing 'then' expression in 'if'")
        expthen = expthen.first

        expelse = expr.rest.rest
        if expelse is not None:
            if expelse.rest is not None:
                raise SyntaxError("Extra expression in 'if'")
            expelse = expelse.first

        self.generate_expr(g, cond, keep=True, tail=False)

        if keep is True:
            lbl_then = self.next_label()
            lbl_end = self.next_label()
            g.emit('goto_if_not_false', lbl_then)
            if expelse is None:
                g.emit('push_nil')
                if tail:
                    g.emit('ret')
            else:
                self.generate_expr(g, expelse, keep=True, tail=tail)
            if not tail:
                g.emit('goto', lbl_end)
            g.def_label(lbl_then)
            self.generate_expr(g, expthen, keep=True, tail=tail)
            g.def_label(lbl_end)
        else:
            if expelse is None:
                lbl_end = self.next_label()
                g.emit('goto_if_false', lbl_end)
                self.generate_expr(g, expthen, keep=False, tail=False)
                g.def_label(lbl_end)
            else:
                lbl_then = self.next_label()
                lbl_end = self.next_label()
                g.emit('goto_if_not_false', lbl_then)
                self.generate_expr(g, expelse, keep=False, tail=False)
                g.emit('goto', lbl_end)
                g.def_label(lbl_then)
                self.generate_expr(g, expthen, keep=False, tail=False)
                g.def_label(lbl_end)

    def generate_lambda(self, base_generator, expr, keep=True, tail=False):
        if keep is not True:
            return  # lambda expression has no side-effect
        try:
            arglst = expr.first
            body = expr.rest

            if isinstance(arglst, pair):
                args = []
                while isinstance(arglst, pair):
                    args.append(arglst.first.name)
                    arglst = arglst.rest
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
            self.generate_body(g, body, keep=True, tail=True)
            base_generator.emit("make_lambda")
            
            if tail:
                base_generator.emit('ret')

        except AttributeError:
            raise SyntaxError("Broken lambda expression")
        
    def generate_define(self, g, expr, keep=True, tail=False):
        if expr is None:
            raise SyntaxError("Empty define expression")
        var = expr.first
        
        if isinstance(var, pair):
            gen = self.generate_lambda
            val = pair(var.rest, expr.rest)
            var = var.first
        elif isinstance(var, sym):
            gen = self.generate_expr
            val = expr.rest
            if val is None:
                raise SyntaxError("Missing value for defined variable")
            if val.rest is not None:
                raise SyntaxError("Extra expressions in 'define'")
            val = val.first
        else:
            raise SyntaxError("Invalid define expression")

        # first define local, then generate value. This allow
        # recursive function to be compiled properly.
        g.def_local(var.name)
        gen(g, val, keep=True, tail=False)
        if keep is True:
            g.emit('dup')
        g.emit_local('set', var.name)
        if tail:
            g.emit('ret')

    def generate_set_x(self, g, expr, keep=True, tail=False):
        if expr is None:
            raise SyntaxError("Empty set! expression")
        var = expr.first

        if not isinstance(var, sym):
            raise SyntaxError("Invalid set! expression, expecting symbol")
        val = expr.rest

        if val is None:
            raise SyntaxError("Missing value for set! expression")
        if val.rest is not None:
            raise SyntaxError("Extra expressions in 'set!'")
        val = val.first

        self.generate_expr(g, val, keep=True, tail=False)
        if keep:
            g.emit('dup')
        g.emit_local('set', var.name)
        if tail:
            g.emit('ret')

    def generate_quote(self, g, expr, keep=True, tail=False):
        if keep:
            g.emit('push_literal', expr.first)
        if tail:
            g.emit('ret')
