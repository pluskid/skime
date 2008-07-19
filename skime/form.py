from .errors import MiscError
from .env    import Environment

class Form(object):
    """\
    A Form is the result of compiling an expression.
    """
    def __init__(self, builder, bytecode):
        # The bytecode of this form
        self.bytecode = bytecode

    def eval(self, env):
        "Eval the form under env."
        ctx = Context(self, env)
        ctx.run()
        return ctx.pop()
