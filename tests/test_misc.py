from helper import HelperVM

class TestOverlappedContextSwitch(HelperVM):
    """\
    Test context switch: skime -> python -> skime
    """
    def test_ctx_switch(self):
        code = """
        (begin
            (define (myadd a b) (+ a b))
            (define (foo n)
                ; apply is a Python primitive
                ; myadd is a skime lambda
                (apply myadd '(1 2))
                (+ n 4))
            (foo 10))
        """
        assert self.eval(code) == 14

