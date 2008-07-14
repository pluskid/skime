# Test for built-in special forms
from skime.vm import VM
from skime.compiler.compiler import Compiler
from skime.compiler.parser import parse
from skime.types.symbol import Symbol as sym

from skime.errors import SyntaxError

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

    def test_define(self):
        assert self.eval("(begin (define foo 5) foo)") == 5
        assert_raises(SyntaxError, self.eval, "(define)")
        assert_raises(SyntaxError, self.eval, "(define foo)")
        assert_raises(SyntaxError, self.eval, "(define foo 5 6)")

        assert self.eval("(begin (define (foo x) x) (foo 5))") == 5
        assert self.eval("(begin (define (foo)) (foo))") == None
