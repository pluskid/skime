from .errors import WrongArgNumber

class Procedure(object):
    def __init__(self, argc, fixed_argc, locals, literals, bytecode):
        self.lexical_parent = None
        self.argc = argc
        self.fixed_argc = fixed_argc
        self.locals = locals
        self.literals = literals
        self.bytecode = bytecode

    def check_arity(self, argc):
        if self.fixed_argc == self.argc:
            if argc != self.argc:
                raise WrongArgNumber("Expecting %d arguments, but got %d" %
                                     (self.argc, argc))
        else:
            if argc < self.fixed_argc:
                raise WrongArgNumber("Expecting at least %d arguments, but got %d" %
                                     (self.fixed_argc, argc))

