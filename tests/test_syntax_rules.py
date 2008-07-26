import helper

from skime.macro import Macro, DynamicClosure
from skime.compiler.parser import parse
from skime.types.pair import Pair as pair
from skime.errors import SyntaxError

from nose.tools import assert_raises

def filter_dc(expr):
    if isinstance(expr, DynamicClosure):
        return filter_dc(expr.expression)
    if isinstance(expr, pair):
        return pair(filter_dc(expr.first),
                    filter_dc(expr.rest))
    return expr

def macro(code):
    return Macro(None, parse(code))
def trans(m, expr):
    return filter_dc(m.transform(None, parse(expr))[0])

class TestSyntaxRules(object):
    """\
    Test syntax rules transformation without touching the env and
    lexical scoping related stuff.
    """
    def test_variable(self):
        m = macro("(() ((_ a) a))")
        assert trans(m, "(_ 5)") == 5
        assert trans(m, "(_ (1 2))") == pair(1, pair(2, None))
        assert_raises(SyntaxError, trans, m, "(_ 1 2)")

    def test_constant(self):
        m = macro("(() ((_ 0 a b) a) ((_ 1 a b) b))")
        assert trans(m, "(_ 0 5 6)") == 5
        assert trans(m, "(_ 1 5 6)") == 6
        assert_raises(SyntaxError, trans, m, ("(_ 2 5 6)"))

    def test_proper_list(self):
        m = macro("(() ((_ a) a) ((_ a b) b) ((_ a b c) c))")
        assert trans(m, "(_ 1)") == 1
        assert trans(m, "(_ 1 2)") == 2
        assert trans(m, "(_ 1 2 3)") == 3
        assert_raises(SyntaxError, trans, m, ("(_)"))

    def test_improper_list(self):
        m = macro("(() ((_ a . b) b))")
        assert trans(m, "(_ 1)") == None
        assert trans(m, "(_ 1 2)") == pair(2, None)
        assert trans(m, "(_ 1 . 2)") == 2
        assert trans(m, "(_ 1 . (2 3))") == pair(2, pair(3, None))
        assert_raises(SyntaxError, trans, m, "(_)")

        m = macro("(() ((_ a . 2) a))")
        assert trans(m, "(_ 5 . 2)") == 5
        assert_raises(SyntaxError, trans, m, "(_ 5 2)")
        assert_raises(SyntaxError, trans, m, "(_ 5 . 3)")

    def test_variable_ellipsis(self):
        m = macro("(() ((_ a ...) ((a) ...)))")
        assert trans(m, "(_)") == None
        assert trans(m, "(_ 1)") == parse("((1))")
        assert trans(m, "(_ 1 2)") == parse("((1) (2))")
        assert_raises(SyntaxError, trans, m, "(_ 1 . 2)")

    def test_constant_ellipsis(self):
        m = macro("(() ((_ a b 2 ...) a) ((_ a b 2 ... c) b))")
        assert trans(m, "(_ 5 6)") == 5
        assert trans(m, "(_ 5 6 2)") == 5
        assert trans(m, "(_ 5 6 2 2)") == 5
        assert trans(m, "(_ 5 6 3)") == 6
        assert trans(m, "(_ 5 6 2 3)") == 6
        assert trans(m, "(_ 5 6 2 2 3)") == 6

    def test_sequence_ellipsis(self):
        m = macro("(() ((_ (a b) ...) (a ... b ...)))")
        assert trans(m, "(_)") == None
        assert trans(m, "(_ (1 2))") == parse("(1 2)")
        assert trans(m, "(_ (1 2) (3 4))") == parse("(1 3 2 4)")

    def test_ellipsis(self):
        m = macro("(() ((_ (a ...) ...) ((a) ... ...)))")
        assert trans(m, "(_)") == None
        assert trans(m, "(_ ())") == None
        assert trans(m, "(_ (1))") == parse("((1))")
        assert trans(m, "(_ (1 2))") == parse("((1) (2))")
        assert trans(m, "(_ (1 2) (3))") == parse("((1) (2) (3))")
        assert trans(m, "(_ (1 2) () (3))") == parse("((1) (2) (3))")

    def test_combined_ellipsis(self):
        m = macro("(() ((_ (a ...) (b ...)) ((a b) ...)))")
        assert trans(m, "(_ () ())") == None
        assert trans(m, "(_ (1 2) (3 4))") == parse("((1 3) (2 4))")
        assert_raises(SyntaxError, trans, m, "(_ (1) (3 4))")
        assert_raises(SyntaxError, trans, m, "(_ (1 2) (3))")

    # R5RS doesn't require this, but we support it
    def test_ellipsis_with_improper_list(self):
        m = macro("(() ((_ a ... . b) b))")
        assert trans(m, "(_ . 6)") == 6
        assert trans(m, "(_ 5 . 6)") == 6
        assert trans(m, "(_ 5 6 . 6)") == 6
        
