from .types.pair   import Pair as pair
from .types.symbol import Symbol as sym
from .errors       import SyntaxError

class Macro(object):
    def __init__(self, env, body):
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
            raise SyntaxError("Expecting (pattern template) for syntax rule, but got %s" % rule)
        if rule.rest.rest is not None:
            raise SyntaxError("Extra expressions in syntax rule: %s" % rule)
        self.matcher = self.compile_pattern(rule.first)
        self.template = rule.rest.first

    def match(self, env, form):
        return False

    def compile_pattern(self, pattern):
        """\
        Compile pattern into a matcher.
        """
        pass

########################################
# Pattern matching
########################################
class MatchError(Exception):
    pass

class MatchDict(dict):
    """\
    A MatchDict hold the matched value of variable patterns. It is an error to
    have duplicated variable patterns with the same name.
    """
    def __setitem__(self, key, value):
        if self.has_key(key):
            raise SyntaxError("Duplicated variable pattern in macro: %s" % key)
        dict.__setitem__(self, key, value)
    def __str__(self):
        return "<MatchDict %s>" % dict.__str__(self)

class Ellipsis(list):
    """\
    Ellipsis holds the zero or more value of an ellipsis pattern.
    """
    def __init__(self, *value):
        list.__init__(self, value)
    def __repr__(self):
        return "<Ellipsis %s>" % list.__repr__(self)

class EllipsisMatchDict(dict):
    """\
    Like MatchDict, excpet that all values are Ellipsis. Thus duplicated
    item assignments are allowed, and automatically append to the corresponding
    Ellipsis. However, the duplication will still be check for the parent
    dict.
    """
    def __init__(self, parent):
        self.parent = parent
    def __setitem__(self, key, value):
        el = self.get(key)
        if el is None:
            # no such key yet, check parent for duplication first
            d = self
            while isinstance(d, EllipsisMatchDict):
                d = d.parent
                if d.has_key(key):
                    raise SyntaxError("Duplicated variable pattern in macro: %s" % key)
            # ok, no duplication, create the Ellipsis
            dict.__setitem__(self, key, Ellipsis(value))
        else:
            # already has the key
            el.append(value)
    def __str__(self):
        return "<EllipsisMatchDict %s>" % dict.__str__(self)
            

class Matcher(object):
    "The base class for all matchers."
    def __init__(self, name):
        self.name = name
        self.ellipsis = False

    def match(self, expr, match_dict):
        """\
        Match against expr and return the remaining expression.
        If can not match, raise MatchError.
        """
        raise MatchError("%s: match not implemented" % self)

    def __str__(self):
        return '<%s name=%s, ellipsis=%s>' % (self.__class__.__name__,
                                              self.name,
                                              self.ellipsis)

class VariableMatcher(Matcher):
    """\
    A variable match any single expression.
    """
    def match(self, expr, match_dict):
        if self.ellipsis:
            result = Ellipsis()
            while isinstance(expr, pair):
                result.append(expr.first)
                expr = expr.rest
            if expr is not None:
                raise MatchError("%s: matching against an improper list" % self)
        else:
            if not isinstance(expr, pair):
                raise MatchError("%s: unable to match %s" % (self, expr))
            result = expr.first
            expr = expr.rest

        match_dict[self.name] = result
        return expr
        
class UnderscopeMatcher(Matcher):
    """\
    An underscope match any single expression and discard the matched result.
    """
    def match(self, expr, match_dict):
        if self.ellipsis:
            while isinstance(expr, pair):
                expr = expr.rest
            if expr is not None:
                raise MatchError("%s: matching against an improper list" % self)
        else:
            if not isinstance(expr, pair):
                raise MatchError("%s: unable to match %s" % (self, expr))
            expr = expr.rest

        return expr
    
class RestMatcher(Matcher):
    """\
    RestMatcher match against the rest of a list like (a b . c), where c will
    be a RestMatcher.
    """
    def match(self, expr, match_dict):
        # eat the whole thing
        match_dict[self.name] = expr
        return None

class SequenceMatcher(Matcher):
    """\
    SequenceMatcher hold a sequence of matchers and matches them in that order.
    """
    def __init__(self):
        Matcher.__init__(self, None)
        self.sequence = []

    def match(self, expr, match_dict):
        if self.ellipsis:
            md = EllipsisMatchDict(match_dict)
            try:
                while isinstance(expr, pair):
                    self.match_sequence(expr, md)
                    expr = expr.rest
            except MatchError:
                pass
            # merge data in EllipsisMatchDict into match_dict
            match_dict.update(md)
            return expr
        else:
            if not isinstance(expr, pair):
                raise MatchError("%s: unable to match %s" % (self, expr))
            self.match_sequence(expr, match_dict)
            return expr.rest

    def match_sequence(self, expr, match_dict):
        expr = expr.first
        for m in self.sequence:
            expr = m.match(expr, match_dict)
        if expr is not None:
            # not matched expressions
            raise MatchError("%s: ramaining expressions not matched: %s" % (self, expr))
        

    def add_matcher(self, matcher):
        self.sequence.append(matcher)

    def __str__(self):
        return "<SequenceMatcher sequence=[%s], ellipsis=%s>" % (', '.join([m.__str__()
                                                                            for m in self.sequence]),
                                                                 self.ellipsis)
