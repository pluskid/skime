from .pair   import Pair as pair
from .symbol import Symbol as sym
from .errors import SyntaxError

class Macro(object):
    def __init__(self, ctx, body):
        try:
            # Process literals
            literals = body.first

            self.rules = []
            # Process syntax rules
            rules = body.rest
            while rules is not None:
                rule = rules.first
                self.rules.append(SyntaxRule(rule))
                rules = rules.rest
        except AttributeError:
            raise SyntaxError("Invalid syntax for syntax-rules form")

class SyntaxRule(object):
    def __init__(self, rule):
        if not isinstance(rule, pair) or not isinstance(rule.rest, pair):
            raise SyntaxError("Invalid syntax rule, expecting (pattern template)")
        if rule.rest.rest is not None:
            raise SyntaxError("Extra expressions in syntax rule.")
        self.pattern = rule.first
        self.template = rule.rest.first

