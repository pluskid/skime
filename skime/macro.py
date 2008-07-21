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
    def __init__(self, rule, literals):
        if not isinstance(rule, pair) or not isinstance(rule.rest, pair):
            raise SyntaxError("Expecting (pattern template) for syntax rule, but got %s" % rule)
        if rule.rest.rest is not None:
            raise SyntaxError("Extra expressions in syntax rule: %s" % rule)
        self.variables = {}
        self.matcher = self.compile_pattern(rule.first, literals)
        self.template = rule.rest.first

    def match(self, env, form):
        return False

    def compile_pattern(self, pattern, literals):
        """\
        Compile pattern into a matcher.
        """
        if not isinstance(pattern, pair):
            raise SyntaxError("Invalid pattern for macro: %s" % pattern)
        # skip the first element, it should be the macro keyword or underscope
        # NOTE, if some invalid expressions are put here, they will be silently
        # ignored
        pattern = pattern.rest

        return self._compile_pattern(pattern, literals)

    def _compile_pattern(self, pat, literals):
        if isinstance(pat, pair):
            mt = SequenceMatcher()
            while isinstance(pat, pair):
                submt = self._compile_pattern(pat.first, literals)
                mt.add_matcher(submt)
                pat = pat.rest
                if isinstance(pat, pair) and pat.first == sym('...'):
                    submt.ellipsis = True
                    pat = pat.rest
            if pat is not None:
                submt = self._compile_pattern(pat, literals)
                mt.add_matcher(RestMatcher(submt))
            return mt

        if isinstance(pat, sym):
            if pat in literals:
                return LiteralMatcher(pat.name)
            if pat == sym('_'):
                return UnderscopeMatcher()
            if self.variables.get(pat.name) is not None:
                raise SyntaxError("Duplicated variable in macro: %s" % pat)
            self.variables[pat.name] = True
            return VariableMatcher(pat.name)

        return ConstantMatcher(pat)

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
    Like MatchDict, excpet that all values are Ellipsis.
    """
    def __setitem__(self, key, value):
        el = self.get(key)
        if el is None:
            # no such key yet
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

class LiteralMatcher(Matcher):
    # TODO: implement this
    pass

class ConstantMatcher(Matcher):
    """\
    Matches any constant.
    """
    def __init__(self, value):
        Matcher.__init__(self, None)
        self.value = value
    def match(self, expr, match_dict):
        if not isinstance(expr, pair) or \
           pair.first != self.value:
            raise MatchError("%s: can not match %s" % (self, expr))
        return expr.rest
    def __str__(self):
        return "<ConstantMatcher value=%s, ellipsis=%s>" % (self.value, self.ellipsis)

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
    def __init__(self):
        Matcher.__init__(self, '_')
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
    be a RestMatcher. The matcher is implemented by wrapping another matcher.
    """
    def __init__(self, matcher):
        self.matcher = matcher
    def match(self, expr, match_dict):
        return self.matcher.match(pair(expr, None), match_dict)
    def __str__(self):
        return "<RestMatcher: matcher=%s>" % self.matcher

class SequenceMatcher(Matcher):
    """\
    SequenceMatcher hold a sequence of matchers and matches them in that order.
    """
    def __init__(self):
        Matcher.__init__(self, None)
        self.sequence = []

    def match(self, expr, match_dict):
        if self.ellipsis:
            md = EllipsisMatchDict()
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
