from vm import VM
from ctx import Context
from proc import Procedure
from codec import encode
from compiler import Generator

if __name__ == '__main__':
    vm = VM()

    gs = Generator(parent=vm.ctx)
    gs.def_local('fact')
    g = gs.push_proc(args=['n'])
    gs.emit('make_lambda')
    gs.emit('set_local', 'fact')
    gs.emit('push_literal', 5)
    gs.emit('push_local', 'fact')
    gs.emit('call', 1)

    g.emit('push_local', 'n')
    g.emit('push_1')
    g.emit('test_equal')
    g.emit('goto_if_true', 'ret_1')
    g.emit('push_1')
    g.emit('push_local', 'n')
    g.emit('minus')
    g.emit('push_local_depth', 1, 'fact')
    g.emit('call', 1)
    g.emit('push_local', 'n')
    g.emit('push_local_depth', 2, '*')
    g.emit('call', 2)
    g.emit('goto', 'ret')
    g.def_label('ret_1')
    g.emit('push_1')
    g.def_label('ret')
    g.emit('ret')

    script = gs.generate()
    
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

    script.lexical_parent = vm.ctx

    vm.run(script)

    print vm.ctx.pop()
