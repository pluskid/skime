from cStringIO import StringIO

from .errors import WrongArgNumber
from .iset   import INSTRUCTIONS

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
        
        self.bytecode = builder.bytecode

        self.argc = len(builder.args)
        self.rest_arg = builder.rest_arg

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
        io.write(', '.join(self.locals[:self.fixed_argc]))
        if self.fixed_argc != self.argc:
            if self.argc == 1:
                io.write('*'+self.locals[0])
            else:
                io.write(', *' + self.locals[self.argc-1])
        io.write('\n')

        io.write("literals:\n")
        for i in range(len(self.literals)):
            io.write("%4d: %s\n" % (i, self.literals[i]))

        io.write("\ninstructions:\n")
        io.write('-'*50)
        io.write('\n')

        ip = 0
        while ip < len(self.bytecode):
            io.write("%04X " % ip)
            instr = INSTRUCTIONS[self.bytecode[ip]]
            io.write("%20s " % instr.name)
            if instr.name in ['push_local', 'set_local']:
                io.write('name=')
                io.write(self.locals[self.bytecode[ip+1]])
            elif instr.name in ['push_local_depth', 'set_local_depth']:
                depth = self.bytecode[ip+1]
                idx = self.bytecode[ip+2]
                io.write("depth=%d, idx=%d" % (depth, idx))
                try:
                    ctx = self.lexical_parent
                    while depth > 1:
                        ctx = ctx.parent
                        depth -= 1
                        io.write(" (name=%s)" % ctx.get_local_name(idx))
                except AttributeError:
                    # The lexical parent chain may not available until runtime
                    # (see make_lambda instruction). In that case, finding the
                    # name of depth-local variable is impossible.
                    pass
            elif instr.name in ['goto', 'goto_if_not_false', 'goto_if_false']:
                io.write("ip=0x%04X" % self.bytecode[ip+1])
            else:
                io.write(', '.join(["%s=%s" % (name, val)
                                    for name, val in zip(instr.operands,
                                                         self.bytecode[ip+1:
                                                                       ip+len(instr.operands)+1])]))
            io.write('\n')
            ip += instr.length


        content = io.getvalue()
        io.close()

        return content
