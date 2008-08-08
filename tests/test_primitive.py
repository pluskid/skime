from helper import HelperVM

from skime.errors       import WrongArgType
from skime.errors       import WrongArgNumber
from skime.errors       import MiscError

from skime.types.pair   import Pair as pair
from skime.types.symbol import Symbol as sym

from nose.tools import assert_raises

class TestArithmetic(HelperVM):
    def test_basic(self):
        assert self.eval('(+ 1 2 3)') == 6
        assert self.eval('(+ -1 1)') == 0
        assert self.eval('(+ 1)') == 1
        assert self.eval('(+)') == 0
        assert_raises(WrongArgType, self.eval, '(+ 1 "foo")')

        assert self.eval('(- 3 2 1)') == 0
        assert self.eval('(- 2 1)') == 1
        assert self.eval('(- 2)') == -2
        assert_raises(WrongArgNumber, self.eval, '(-)')

        assert self.eval('(* -2 -3)') == 6
        assert self.eval('(* 2)') == 2
        assert self.eval('(*)') == 1

        assert self.eval('(/ 6 3)') == 2
        # skime has no rational type, divid is
        # done in float type
        assert self.eval('(/ 2)') == 0.5
        assert self.eval('(/ 2.0)') == 0.5
        assert_raises(WrongArgNumber, self.eval, '(/)')

class TestLogic(HelperVM):
    def test_logic(self):
        assert self.eval('(= 1 1)') == True
        assert self.eval('(not (= 1 1))') == False
        
        assert self.eval('(not #t)') == False
        assert self.eval('(not #f)') == True
        assert self.eval("(not '())") == False
        assert self.eval("(not 0)") == False

        assert self.eval("(or)") == False
        assert self.eval("(or 1 2 3)") == 1
        assert self.eval("(or #f 2)") == 2
        assert self.eval("(or #f #f)") == False
        assert self.eval("""(begin
                              (define foo 2)
                              (or #f (set! foo 3) (set! foo 4))
                              foo)""") == 3

        assert self.eval("(and)") == True
        assert self.eval("(and #t)") == True
        assert self.eval("(and 1 2 3)") == 3
        assert self.eval("(and #t 2)") == 2
        assert self.eval("""(begin
                              (define foo 2)
                              (and #t (set! foo 3) (set! foo 4))
                              foo)""") == 4

    def test_compare(self):
        assert self.eval('(< -1 1)') == True
        assert self.eval('(< -1 -1)') == False
        assert self.eval('(< 1 2 3 4 5)') == True
        assert self.eval('(< 1 2 3 4 4)') == False

        assert self.eval('(> 1 -1)') == True
        assert self.eval('(> -1 -1)') == False
        assert self.eval('(> 5 4 3 2 1)') == True
        assert self.eval('(> 5 4 3 1 1)') == False

        assert self.eval('(<= -1 1)') == True
        assert self.eval('(<= -1 -1)') == True
        assert self.eval('(<= 1 2 3 4 5)') == True
        assert self.eval('(<= 1 2 3 4 4)') == True
        assert self.eval('(<= 2 1)') == False

        assert self.eval('(>= 1 -1)') == True
        assert self.eval('(>= -1 -1)') == True
        assert self.eval('(>= 5 4 3 2 1)') == True
        assert self.eval('(>= 5 4 3 1 1)') == True
        assert self.eval('(>= 1 2)') == False

class TestList(HelperVM):
    def test_pair(self):
        assert self.eval('(pair 1 2)') == pair(1, 2)
        assert self.eval('(cons 1 2)') == pair(1, 2)
        assert self.eval('(first (pair 1 2))') == 1
        assert self.eval('(car (pair 1 2))') == 1
        assert self.eval('(rest (pair 1 2))') == 2
        assert self.eval('(cdr (pair 1 2))') == 2

        assert self.eval("""(begin (define foo (pair 1 2))
                                   (set-car! foo 3)
                                   foo)""") == pair(3, 2)
        assert self.eval("""(begin (define foo (pair 1 2))
                                   (set-cdr! foo 3)
                                   foo)""") == pair(1, 3)

    def test_list(self):
        assert self.eval('(list 1 2 3)') == pair(1, pair(2, pair(3, None)))

class TestPridict(HelperVM):
    def test_type_predict(self):
        assert self.eval('(boolean? #t)') == True
        assert self.eval('(boolean? (= 1 2))') == True
        assert self.eval('(pair? (pair 1 2))') == True
        assert self.eval('(pair? #t)') == False
        assert self.eval("(symbol? 'foo)") == True
        assert self.eval("(symbol? 2)") == False
        assert self.eval('(string? "foo")') == True
        assert self.eval('(string? 2)') == False
        assert self.eval('(number? 2)') == True
        assert self.eval('(number? 2.0)') == True
        assert self.eval('(number? 2+3i)') == True

        assert self.eval('(procedure? pair)') == True
        assert self.eval('(procedure? (lambda (x) x))') == True
        assert self.eval('(procedure? 5)') == False

class TestApply(HelperVM):
    def test_apply(self):
        assert self.eval('(apply +)') == 0
        assert self.eval("(apply + 1 '())") == 1
        assert self.eval("(apply + '(1))") == 1
        assert self.eval("(apply + (list 1))") == 1
        assert self.eval("(apply + 1 '(2))") == 3
        assert self.eval("(apply - 3 '(2 1))") == 0
        assert self.eval("(apply (lambda (x) x) 1 '())") == 1
        assert_raises(WrongArgNumber, self.eval, "(apply (lambda (x) x) 1 '(2))")
        assert self.eval("(apply (lambda x x) 1 '(2 3))") == pair(1, pair(2, pair(3, None)))

class TestMap(HelperVM):
    def test_map(self):
        assert self.eval("(map + '(1 2) '(3 4))") == pair(4, pair(6, None))
        assert self.eval("(map + '(1 2 3))") == pair(1, pair(2, pair(3, None)))
        assert self.eval("(map (lambda (x y) (pair x y)) '(1 2) '(3 4))") == \
               pair(pair(1, 3), pair(pair(2, 4), None))
        assert_raises(WrongArgNumber, self.eval, "(map (lambda (x y) (pair x y)) '(1 2))")
        assert_raises(WrongArgType, self.eval, "(map + '(1 2 3 . 4))")
        assert_raises(MiscError, self.eval, "(map + '(1 2) '(3 4 5))")
