# A Scheme expression is compiled into a Form. The Form object hold the
# bytecode of the expression. To evaluate the form, a new Context is set up.
# Instruction pointer and operand stack are held in the Context object.
# Local variables are held in an Environment object, which are chained
# through the lexical scope.

from .ctx         import Context
from .env         import Environment
from .            import insns
from .types.pair  import Pair
from .proc        import Procedure
from .prim        import Primitive, load_primitives
from .insns       import run
from .types.pair  import Pair as pair

from .errors      import MiscError

class VM(object):

    def __init__(self):
        self.env = Environment()
        self.env.vm = self
        load_primitives(self.env)

        self.ctx = Context(None, self.env, None)

    def run(self, form):
        return form.eval(self.env)

    def apply(self, proc, args):
        if isinstance(proc, Procedure):
            proc.check_arity(len(args))

            ctx = Context(proc, proc.env.dup(), self.ctx)
            for i in range(proc.fixed_argc):
                ctx.env.assign_local(i, args[i])
            if proc.fixed_argc != proc.argc:
                rest = None
                for i in range(len(args)-proc.fixed_argc):
                    rest = Pair(args[i+proc.fixed_argc], rest)
                ctx.env.assign_local(proc.fixed_argc, rest)

            self.ctx = ctx
            run(self)
            return self.ctx.pop()
        
        elif isinstance(proc, Primitive):
            proc.check_arity(len(args))
            return proc.call(*args)
        
        else:
            raise MiscError("Not a skime callable: %s" % proc)
