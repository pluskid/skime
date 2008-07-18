from .errors import MiscError

class Form(object):
    """\
    A Form is the result of compiling an expression.
    """
    def __init__(self, env, bytecode):
        # The lexical environment of the form
        self.env = env

        # The bytecode of this form
        self.bytecode = bytecode

    def eval(self, env):
        "Eval the form under env."
        ctx = Context(self, env)
        ctx.run()
        return ctx.pop()
