from helper import HelperVM

from skime.types.pair import Pair as pair

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

    def test_basic_recursive(self):
        assert self.eval("""
        (begin
          (define-syntax my-add (syntax-rules ()
                                  ((_ a) a)
                                  ((_ a b c ...) (my-add (+ a b) c ...))))
          (my-add 1 2 3 4 5))""") == 15

    def test_basic_literal(self):
        assert self.eval("""
        (begin
          (define <-> 5)
          (define-syntax my-syntax (syntax-rules (<->)
                                     ((_ a <-> b) (list b a))))
          ; assignment doesn't change lexical binding
          (set! <-> 6)
          (my-syntax 3 <-> 4))""") == pair(4, pair(3, None))

    def test_basic_lexical_scope(self):
        assert self.eval("""
        (begin
          (define-syntax my-add (syntax-rules ()
                                  ((_ a b) (+ a b))))
          (define (my-proc x)
            (my-add x x))

          (my-proc 5))""") == 10

    def test_lexical_scope(self):
        assert self.eval("""
        (begin
          (define-syntax swap
                         (syntax-rules ()
                           ((swap a b)
                            ((lambda (tmp)
                               (set! a b)
                               (set! b tmp))
                             a))))
          (define foo 4)
          (define tmp 5)
          (swap foo tmp)
          (cons foo tmp))""") == pair(5, 4)

        assert self.eval("""
        (begin
          (define foo 10)
          (define-syntax stx (syntax-rules ()
                               ((_ a) (cons a foo))))
          ((lambda (foo)
             (stx foo))
           100))""") == pair(100, 10)

        assert self.eval("""
        (begin
          (define-syntax def10 (syntax-rules ()
                                 ((_ var) (define var 10))))
          (def10 foo)
          foo)""") == 10
