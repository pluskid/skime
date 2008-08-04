# A Scheme expression is compiled into a Form. The Form object hold the
# bytecode of the expression. To evaluate the form, a new Context is set up.
# Instruction pointer and operand stack are held in the Context object.
# Local variables are held in an Environment object, which are chained
# through the lexical scope.

import os.path

from .ctx               import Context
from .env               import Environment
from .                  import insns
from .types.pair        import Pair
from .proc              import Procedure
from .prim              import Primitive, load_primitives
from .insns             import run
from .types.pair        import Pair as pair

from .compiler.parser   import parse
from .compiler.compiler import Compiler

from .errors            import WrongArgType

class VM(object):

    def __init__(self):
        self.compiler = Compiler()
        
        self.env = Environment()
        self.env.vm = self
        load_primitives(self.env)

        self.ctx = Context(None, self.env, None)

        self.load(os.path.join(os.path.dirname(__file__),
                               'scheme',
                               'prim.scm'))

    def run(self, form):
        return form.eval(self.env, self)

    def load(self, path):
        io = open(path)
        content = io.read()
        io.close()

        return self.eval_string("(begin %s)" % content)

    def eval_string(self, script):
        return self.run(self.compiler.compile(parse(script), self.env))

    def apply(self, proc, args):
        if isinstance(proc, Procedure):
            proc.check_arity(len(args))

            ctx = Context(proc, proc.env.dup(), self.ctx)
            for i in range(proc.fixed_argc):
                ctx.env.assign_local(i, args[i])
            if proc.fixed_argc != proc.argc:
                rest = None
                for i in range(len(args)-1, proc.fixed_argc-1, -1):
                    rest = Pair(args[i], rest)
                ctx.env.assign_local(proc.fixed_argc, rest)

            return run(ctx)
        
        elif isinstance(proc, Primitive):
            proc.check_arity(len(args))
            return proc.call(self, *args)
        
        else:
            raise WrongArgType("Not a skime callable: %s" % proc)
