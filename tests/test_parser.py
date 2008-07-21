import helper

from skime.compiler.parser import parse as p
from skime.errors import ParseError
from skime.types.symbol import Symbol as sym
from skime.types.pair import Pair as pair

from nose.tools import assert_almost_equal
from nose.tools import assert_raises

class TestNumber(object):
    def test_integer(self):
        assert p('0') == 0
        assert p('5') == 5
        assert p('+10') == 10
        assert p('-10') == -10

    def test_float(self):
        assert_almost_equal(p('0.0'), 0.0)
        assert_almost_equal(p('-0.0'), 0.0)
        assert_almost_equal(p('2.5'), 2.5)
        assert_almost_equal(p('-200.75'), -200.75)

    def test_complex(self):
        assert p('0+i') == 1j
        assert p('5+3i') == 5+3j
        assert p('6-2i') == 6-2j
        assert p('3.5-4i') == 3.5-4j
        assert p('0.3+0.5i') == 0.3+0.5j
        assert p('0.5+0i') == 0.5

    # currently rational numbers are converted to
    # float
    def test_rational(self):
        assert p('6/3') == 2
        assert_almost_equal(p('1/3'), 1.0/3)

class TestString(object):
    def test_string(self):
        assert p('"foo"') == "foo"
        assert p(r'"foo\"bar"') == 'foo"bar'
        assert p(r'"foo\"bar\""') == 'foo"bar"'
        assert p(r'""') == ''
        assert p(r'"tab\t"') == 'tab\t'
        assert p(r'"newline\n"') == 'newline\n'

class TestSymbol(object):
    def test_symbol(self):
        assert p('foo') == sym('foo')
        assert p('foo123') == sym('foo123')
        assert p('string->number') == sym('string->number')
        assert p('number?') == sym('number?')
        assert p('...') == sym('...')

class TestBool(object):
    def test_bool(self):
        assert p('#t') == True
        assert p('#f') == False

class TestPair(object):
    def test_list(self):
        assert p('(1 2 3)') == pair(1, pair(2, pair(3, None)))
        assert p('(1)') == pair(1, None)
        assert p('()') == None

    def test_pair(self):
        assert p('(1 . 2)') == pair(1, 2)
        assert p('(1 .2)') == pair(1, 2)
        assert p('(1 2 . 3)') == pair(1, pair(2, 3))
    
    def test_fail(self):
        assert_raises(ParseError, p, '(')
        assert_raises(ParseError, p, '(1 . 2 3)')
        assert_raises(ParseError, p, '(1))')


class TestQuote(object):
    def test_quote(self):
        assert p("'1") == pair(sym('quote'), pair(1, None))
        assert p("''1") == pair(sym('quote'),
                                pair(pair(sym('quote'),
                                          pair(1, None)),
                                     None))
    def test_quasiquote(self):
        assert p("`1") == pair(sym('quasiquote'), pair(1, None))
        assert p("`,1") == pair(sym('quasiquote'),
                                pair(pair(sym('unquote'),
                                          pair(1, None)),
                                     None))
        assert p("`(1 ,(+ 1 5) ,@(list 1 2))") == \
               pair(sym("quasiquote"),
                    pair(pair(1,
                              pair(pair(sym("unquote"),
                                        pair(pair(sym("+"),
                                                  pair(1,
                                                       pair(5, None))),
                                                None)),
                                   pair(pair(sym("unquote-slicing"),
                                             pair(pair(sym("list"),
                                                       pair(1,
                                                            pair(2, None))),
                                                  None)),
                                        None))),
                         None))

class TestComment(object):
    def test_comment(self):
        assert p("; this is a comment\n5") == 5
        assert p("; this is a comment\n    5") == 5
        assert p("5; this is a comment") == 5
        assert p("5; this is a comment\n") == 5

    def test_pure_comment(self):
        assert_raises(ParseError, p, "; this is only comnent")
        assert_raises(ParseError, p, "; this is only comnent\n")
        assert_raises(ParseError, p, "\n\n  ; this is only comnent\n\n")
