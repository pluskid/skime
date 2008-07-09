from sys import stdout
from vm import VM
from ctx import Context
from proc import Procedure
from codec import encode
from symbol import Symbol as sym
from cons import Cons as cons
from compiler import Generator, Compiler
from parser import Parser

def list2cons(lst):
    if type(lst) is not list:
        return lst
    c = None
    for x in reversed(lst):
        c = cons(list2cons(x), c)
    return c

def pp_sexp(sexp):
    if type(sexp) is sym:
        stdout.write(sexp.name)
    elif type(sexp) in [int, long, float]:
        stdout.write(str(sexp))
    elif type(sexp) in [str, unicode]:
        stdout.write(sexp.__repr__())
    elif sexp is None:
        pass
    elif type(sexp) is cons:
        stdout.write('(')
        pp_sexp(sexp.car)
        cdr = sexp.cdr
        while type(cdr) is cons:
            stdout.write(' ')
            pp_sexp(cdr.car)
            cdr = cdr.cdr
        if cdr is None:
            stdout.write(')')
        else:
            pp_sexp(cdr)
            stdout.write(')')

if __name__ == '__main__':
#     vm = VM()

#     gs = Generator(parent=vm.ctx)
#     gs.def_local('fact')
#     g = gs.push_proc(args=['n'])
#     gs.emit('make_lambda')
#     gs.emit('set_local', 'fact')
#     gs.emit('push_literal', 5)
#     gs.emit('push_local', 'fact')
#     gs.emit('call', 1)

#     g.emit('push_local', 'n')
#     g.emit('push_1')
#     g.emit('test_equal')
#     g.emit('goto_if_true', 'ret_1')
#     g.emit('push_1')
#     g.emit('push_local', 'n')
#     g.emit('minus')
#     g.emit('push_local_depth', 1, 'fact')
#     g.emit('call', 1)
#     g.emit('push_local', 'n')
#     g.emit('push_local_depth', 2, '*')
#     g.emit('call', 2)
#     g.emit('goto', 'ret')
#     g.def_label('ret_1')
#     g.emit('push_1')
#     g.def_label('ret')
#     g.emit('ret')

#     script = gs.generate()
    
# #     proc = Procedure()
# #     proc.bytecode = encode(["push_local", 0,
# #                             "push_1",
# #                             "equal",
# #                             "goto_if_true", 18,
# #                             "push_1",
# #                             "push_local", 0,
# #                             "minus",
# #                             "call", 0, 1,
# #                             "push_local", 0,
# #                             "multiply",
# #                             "goto", 19,
# #                             "push_1",
# #                             "ret"])
# #    proc.literals = ['fact']

#     script.lexical_parent = vm.ctx

#     vm.run(script)

#     print vm.ctx.pop()


    vm = VM()
    compiler = Compiler()
#     sexp = [sym("begin"),
#             [sym("if"), [sym('='), [sym('+'), 2, 3], 5, [sym('/'), 10, 2]],
#              [sym("*"), 2, 3, 4, [sym("+"), 1, 2, 3]],
#              100]]
#     sexp = [sym("begin"),
#             [sym("define"), sym("x"), 10],
#             [[sym("lambda"),
#               [sym("a"), sym("b")],
#               [sym("+"), sym("a"), sym("b"), sym("x")]],
#              1, 2]]

    sexp = [sym("begin"),
            [sym("define"), sym("fact"),
             [sym("lambda"), [sym("n")],
              [sym("if"), [sym("="), sym("n"), 0],
               1, [sym("*"), sym("n"),
                   [sym("fact"), [sym("-"), sym("n"), 1]]]]]],
            [sym("fact"), 5]]
    sexp = list2cons(sexp)
    script = compiler.compile(sexp, vm.ctx)

    script.lexical_parent = vm.ctx
    vm.run(script)
    
    print vm.ctx.pop()


    code = '(+ a (/ 2 1 "foo" 34))'
    sexp = Parser(code).parse()
    pp_sexp(sexp)
    print
