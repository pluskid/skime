from vm import VM
from ctx import Context
from proc import Procedure
from codec import encode
from compiler import Generator

if __name__ == '__main__':
    vm = VM()

    gs = Generator()
    gs.def_local('fact')
    
    g = Generator(parent=gs, args=['n'])
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
    g.emit('multiply')
    g.emit('goto', 'ret')
    g.def_label('ret_1')
    g.emit('push_1')
    g.def_label('ret')
    g.emit('ret')

    fact = g.generate()

    gs.emit('push_literal', fact)
    gs.emit('make_lambda')
    gs.emit('set_local', 'fact')
    gs.emit('push_literal', 5)
    gs.emit('push_local', 'fact')
    gs.emit('call', 1)

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

    ctx = Context(vm, script)
    vm.ctx = ctx
    vm.ctx.locals = map(lambda x: None, ctx.proc.locals)
    vm.run()

    print vm.ctx.pop()
