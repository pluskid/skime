# A Scheme expression is compiled into a Form. The Form object hold the
# bytecode of the expression. To evaluate the form, a new Context is set up.
# Instruction pointer and operand stack are held in the Context object.
# Local variables are held in an Environment object, which are chained
# through the lexical scope.

from .ctx  import TopLevelContext, Context
from .     import insns
from .proc import Procedure
from .prim import Primitive
from .types.pair import Pair as pair

from .errors import MiscError

class VM(object):

    def __init__(self):
        self.ctx = TopLevelContext(self)

    def run(self, proc, args=[]):
        if isinstance(proc, Procedure):
            proc.check_arity(len(args))
            
            self.ctx = Context(self.ctx, proc)
            for i in range(proc.fixed_argc):
                self.ctx.locals[i] = args[i]
            if proc.fixed_argc != proc.argc:
                rest = None
                for i in range(len(args)-proc.fixed_argc):
                    rest = pair(args[proc.fixed_argc+i], rest)
                proc.locals[proc.fixed_argc] = rest
            
            insns.run(self)
            return self.ctx.pop()

        elif isinstance(proc, Primitive):
            proc.check_arity(len(args))
            return proc.call(*args)

        else:
            raise MiscError("Not a skime callable: %s" % proc)
