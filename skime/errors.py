class Error(Exception):
    "Base class for all exceptions in skime"

class CompileError(Error):
    "Compile errors"

class UnboundVariable(CompileError):
    def __init__(self, name, message):
        Exception.__init__(self, message)
        self.name = name

class WrongArgNumber(CompileError):
    pass

class SyntaxError(CompileError):
    pass

class ParseError(CompileError):
    pass

class MiscError(Error):
    pass

class WrongArgType(Error):
    pass
