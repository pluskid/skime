# Test for built-in special forms
from skime.vm import VM
from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse
from skime.types.symbol import Symbol as sym
from skime.types.cons import Cons as cons

from skime.errors import SyntaxError
from skime.errors import UnboundVariable

from nose.tools import assert_raises

class TestSyntax(object):
    def __init__(self):
        self.compiler = Compiler()
        
    def eval(self, code):
        vm = VM()
        proc = self.compiler.compile(parse(code), vm.ctx)
        return vm.run(proc)

    def test_atom(self):
        assert self.eval("1") == 1
        assert self.eval('"foo"') == "foo"

    def test_begin(self):
        assert self.eval("(begin 1 2 3)") == 3
        assert self.eval("(begin 1)") == 1
        assert self.eval("(begin)") == None

    def test_if(self):
        assert self.eval("(if #t 1 2)") == 1
        assert self.eval("(if #f 1 2)") == 2
        assert self.eval("(if #t 1)") == 1
        assert self.eval("(if #f 1)") == None
        assert_raises(SyntaxError, self.eval, "(if #t)")
        assert_raises(SyntaxError, self.eval, "(if)")
        assert_raises(SyntaxError, self.eval, "(if #t 1 2 3)")

    def test_lambda(self):
        assert self.eval("((lambda (x) x) 5)") == 5
        assert self.eval("((lambda (x) (+ x 1)) 5)") == 6
        assert self.eval("((lambda () 5))") == 5
        assert self.eval("((lambda x (car x)) 1 2)") == 1
        assert self.eval("((lambda x (car x)) 1 2 3 4 5)") == 1
        assert self.eval("((lambda x (car x)) 1)") == 1
        assert self.eval("((lambda (x . y) x) 1)") == 1
        assert self.eval("((lambda (x . y) y) 1)") == None
        assert self.eval("((lambda (x . y) (car y)) 1 2 3)") == 2

    def test_call(self):
        assert self.eval("(- 5 4)") == 1

    def test_define(self):
        assert self.eval("(begin (define foo 5) foo)") == 5
        assert_raises(SyntaxError, self.eval, "(define)")
        assert_raises(SyntaxError, self.eval, "(define foo)")
        assert_raises(SyntaxError, self.eval, "(define foo 5 6)")

        assert self.eval("(begin (define (foo x) x) (foo 5))") == 5
        assert self.eval("(begin (define (foo)) (foo))") == None

        assert self.eval("(begin (define (foo . x) (car x)) (foo 1))") == 1
        assert self.eval("(begin (define (foo . x) (car x)) (foo 1 2))") == 1

    def test_set_x(self):
        assert self.eval("""
(begin
  (define foo 5)
  (define bar foo)
  (set! foo 6)
  (cons foo bar))""") == cons(6, 5)
        assert self.eval("(set! cons 10)") == 10
        assert_raises(UnboundVariable, self.eval, "(set! var-not-exist 10)")
