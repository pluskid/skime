from cStringIO        import StringIO

from .errors          import WrongArgNumber
from .compiler.disasm import disasm

class Procedure(object):
    def __init__(self, builder, bytecode):
        # The lexical parent of the procedure scope. It might be
        # an Environment created at compile time. In that case,
        # a 'make-lambda' instruction will be emitted in the
        # instruction sequence to fix the parent at run time.
        self.lexical_parent = builder.env.parent
        
        # The Environment created at compile time. A new
        # Environment will be created when the procedure
        # is called.
        self.env = builder.env
        
        self.bytecode = bytecode

        self.argc = len(builder.args)
        self.rest_arg = builder.rest_arg

        self.literals = list(builder.literals)

    def check_arity(self, argc):
        if self.rest_arg:
            if argc < self.argc-1:
                raise WrongArgNumber("Expecting at least %d arguments, but got %d" %
                                     (self.argc-1, argc))
        else:
            if argc != self.argc:
                raise WrongArgNumber("Expecting %d arguments, but got %d" %
                                     (self.argc, argc))
                
    def disasm(self):
        "Show the disassemble of the instructions of the proc. Useful for debug."
        io = StringIO()
        io.write('='*60)
        io.write('\n')
        io.write('Diasassemble of proc at %X\n' % id(self))
        
        io.write('arguments: ')
        args = [self.env.get_name(i) for i in range(self.argc)]
        if self.rest_arg:
            args[-1] = '*'+args[-1]
        io.write(', '.join(args))
        io.write('\n')

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
