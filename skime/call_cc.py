from .errors import WrongArgNumber

class Continuation(object):
    def __init__(self, ctx, ip_displacement, n_pop):
        self.ctx = ctx.clone()
        self.ctx.ip += ip_displacement
        if n_pop > 0:
            self.ctx.pop_n(n_pop)

    def __str__(self):
        return '<Continuation ctx=%s>' % self.ctx
