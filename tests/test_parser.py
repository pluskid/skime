from skime.parser import parse as p
from nose.tools import assert_almost_equal

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

    def test_comment(self):
        assert p("; this is a comment\n5") == 5
        assert p("; this is a comment\n    5") == 5
        assert p("5; this is a comment") == 5
        assert p("5; this is a comment\n") == 5

