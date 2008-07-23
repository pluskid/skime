from helper import HelperVM

class TestMacro(HelperVM):
    """\
    Unlike test_syntax_rules, this test case test the macro with
    the skime VM as a whole.
    """

    def test_basic(self):
        assert self.eval("""
        (begin
          (define-syntax my-add (syntax-rules ()
                                  ((_ a b) (+ a b))))
          (my-add 1 2))""") == 3
