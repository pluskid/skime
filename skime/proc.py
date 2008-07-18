from cStringIO import StringIO

from .errors import WrongArgNumber
from .iset   import INSTRUCTIONS

class Procedure(object):
    def __init__(self, argc, fixed_argc, locals, literals, bytecode):
        self.lexical_parent = None
        self.argc = argc
        self.fixed_argc = fixed_argc
        self.locals = locals
        self.literals = literals
        self.bytecode = bytecode

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
            io.write("%-4X " % ip)
            instr = INSTRUCTIONS[self.bytecode[ip]]
            io.write("%20s " % instr.name)
            if instr.name in ['push_local', 'set_local']:
                io.write('name=')
                io.write(self.locals[self.bytecode[ip+1]])
            elif instr.name in ['push_local_depth', 'set_local_depth']:
                depth = self.bytecode[ip+1]
                idx = self.bytecode[ip+2]
                io.write("depth=%d, idx=%d" % (depth, idx))
                ctx = self.lexical_parent
                while depth > 1:
                    ctx = ctx.parent
                    depth -= 1
                io.write(" (name=%s)" % ctx.get_local_name(idx))
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
