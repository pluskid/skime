from ..iset import INSTRUCTIONS


def disasm(io, form):
    bytecode = form.bytecode
    env = form.env
    literals = form.literals
    
    ip = 0
    while ip < len(bytecode):
        io.write("%04X " % ip)
        instr = INSTRUCTIONS[bytecode[ip]]
        io.write("%20s " % instr.name)
        if instr.name in ['push_local', 'set_local']:
            io.write('idx: %d' % bytecode[ip+1])
            io.write(', name: ')
            io.write(env.get_name(bytecode[ip+1]))
        elif instr.name in ['push_local_depth', 'set_local_depth']:
            depth = bytecode[ip+1]
            idx = bytecode[ip+2]
            io.write("depth=%d, idx=%d" % (depth, idx))
            penv = env
            while depth > 0:
                penv = penv.parent
                depth -= 1
            io.write(" (name: %s)" % penv.get_name(idx))
        elif instr.name in ['goto', 'goto_if_not_false', 'goto_if_false']:
            io.write("ip=0x%04X" % bytecode[ip+1])
        elif instr.name == 'dynamic_set_local':
            lit = bytecode[ip-1]
            io.write('idx: %d' % bytecode[ip+1])
            io.write(', name: ')
            io.write(literals[lit].expression.name)
        else:
            io.write(', '.join(["%s=%s" % (name, val)
                                for name, val in zip(instr.operands,
                                                     bytecode[ip+1:
                                                              ip+len(instr.operands)+1])]))
        io.write('\n')
        ip += instr.length
