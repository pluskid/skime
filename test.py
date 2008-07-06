from vm import VM
from ctx import Context
from proc import Procedure
from codec import encode
from compiler import Generator

if __name__ == '__main__':
    vm = VM()

    g = Generator(['n'])
    g.emit('push_local', 'n')
    g.emit('push_1')
    g.emit('equal')
    g.emit('goto_if_true', 'ret_1')
    g.emit('push_1')
    g.emit('push_local', 'n')
    g.emit('minus')
    g.emit('call', 0, 1)
    g.emit('push_local', 'n')
    g.emit('multiply')
    g.emit('goto', 'ret')
    g.def_label('ret_1')
    g.emit('push_1')
    g.def_label('ret')
    g.emit('ret')

    proc = g.generate()
    
#     proc = Procedure()
#     proc.bytecode = encode(["push_local", 0,
#                             "push_1",
#                             "equal",
#                             "goto_if_true", 18,
#                             "push_1",
#                             "push_local", 0,
#                             "minus",
#                             "call", 0, 1,
#                             "push_local", 0,
#                             "multiply",
#                             "goto", 19,
#                             "push_1",
#                             "ret"])
#    proc.literals = ['fact']

    ctx = Context(vm, proc)
    vm.ctx = ctx
    vm.ctx.locals = [5]
    vm.run()

    print ctx.pop()
