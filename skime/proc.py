from io        import StringIO

from .errors          import WrongArgNumber
from .compiler.disasm import disasm

class Procedure(object):
    def __init__(self, builder, bytecode):
        
        # The Environment created at compile time. A new
        # Environment will be created when the procedure
        # is called.
        #
        # self.env.parent (i.e. the lexical parent of the
        # env) might be an Environment created at compile
        # time. In that case, a 'make-lambda' instruction
        # will be emitted in the instruction sequence to
        # fix the parent at run time.
        self.env = builder.env
        
        self.bytecode = bytecode

        self.argc = len(builder.args)
        if builder.rest_arg:
            self.fixed_argc = self.argc-1
        else:
            self.fixed_argc = self.argc

        self.literals = list(builder.literals)

    def lexical_parent_get(self):
        return self.env.parent
    def lexical_parent_set(self, parent):
        self.env.parent = parent
    lexical_parent = property(lexical_parent_get, lexical_parent_set)

    def check_arity(self, argc):
        if self.fixed_argc == self.argc:
            if argc != self.argc:
                raise WrongArgNumber("Expecting %d arguments, but got %d" %
                                     (self.argc, argc))
        else:
            if argc < self.fixed_argc:
                raise WrongArgNumber("Expecting at least %d arguments, but got %d" %
                                     (self.fixed_argc, argc))
                
    def disasm(self):
        "Show the disassemble of the instructions of the proc. Useful for debug."
        io = StringIO()
        io.write('='*60)
        io.write('\n')
        io.write('Diasassemble of proc at %X\n' % id(self))
        
        io.write('arguments: ')
        args = [self.env.get_name(i) for i in range(self.argc)]
        if self.fixed_argc != self.argc:
            args[-1] = '*'+args[-1]
        io.write(', '.join(args))
        io.write('\n')

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
