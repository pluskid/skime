from io        import StringIO

from .errors          import MiscError
from .env             import Environment
from .compiler.disasm import disasm
from .insns           import run
from .ctx             import Context

class Form(object):
    """\
    A Form is the result of compiling an expression.
    """
    def __init__(self, builder, bytecode):
        # The environment under which the form is compiled
        # This is a reference to an Environment that might
        # be shared by many forms. This is only used in
        # debugging to find the local variable names used
        # by this form.
        self.env = builder.env
        
        # The bytecode of this form
        self.bytecode = bytecode

        # The literals used in bytecode
        self.literals = builder.literals

    def eval(self, env, vm):
        "Eval the form under env and vm."
        ctx = Context(self, env, vm.ctx)
        return run(ctx)

    def disasm(self):
        "Show the disassemble of the instructions of the form. Useful for debug."
        io = StringIO()
        io.write('='*60)
        io.write('\n')
        io.write('Diasassemble of form at %X\n' % id(self))

        io.write("literals:\n")
        for i in range(len(self.literals)):
            io.write("%4d: %s\n" % (i, self.literals[i]))

        io.write("\ninstructions:\n")
        io.write('-'*50)
        io.write('\n')

        disasm(io, self)

        content = io.getvalue()
        io.close()

        return content
