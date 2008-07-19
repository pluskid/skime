from cStringIO        import StringIO

from .errors          import MiscError
from .env             import Environment
from .compiler.disasm import disasm

class Form(object):
    """\
    A Form is the result of compiling an expression.
    """
    def __init__(self, builder, bytecode):
        # The environment under which the form is compiled
        self.env = builder.env
        
        # The bytecode of this form
        self.bytecode = bytecode

        # The literals used in bytecode
        self.literals = builder.literals

    def eval(self, env):
        "Eval the form under env."
        ctx = Context(self, env)
        ctx.run()
        return ctx.pop()

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

        disasm(io, self.bytecode, self.env)

        content = io.getvalue()
        io.close()

        return content
