from .types.pair   import Pair as pair
from .types.symbol import Symbol as sym
from .errors       import SyntaxError

class Macro(object):
    def __init__(self, env, body):
        try:
            # Process literals
            literals = body.first
            lit = []
            while isinstance(literals, pair):
                lit.append(literals.first)
                literals = literals.rest
            if literals is not None:
                raise SyntaxError("Invalid syntax rule format: literals should be a proper list.")

            self.rules = []
            # Process syntax rules
            rules = body.rest
            while rules is not None:
                rule = rules.first
                self.rules.append(SyntaxRule(rule, lit, env))
                rules = rules.rest
        except AttributeError:
            raise SyntaxError("Invalid syntax for syntax-rules form")

    def transform(self, env, form):
        for rule in self.rules:
            try:
                md = rule.match(env, form)
                return rule.expand(env, md)
            except MatchError:
                pass
        raise SyntaxError("Can not find syntax rule to match the form %s" % form)

class SyntaxRule(object):
    def __init__(self, rule, literals, env):
        if not isinstance(rule, pair) or not isinstance(rule.rest, pair):
            raise SyntaxError("Expecting (pattern template) for syntax rule, but got %s" % rule)
        if rule.rest.rest is not None:
            raise SyntaxError("Extra expressions in syntax rule: %s" % rule)
        self.env = env
        self.variables = {}
        self.literals = literals
        self.matcher = self.compile_pattern(rule.first)
        self.template = self.compile_template(rule.rest.first)

    def match(self, env, form):
        md = MatchDict()
        if not isinstance(form, pair):
            raise SyntaxError("Invalid macro matching against the form %s" % form)
        # skip the first element, which is the macro keyword
        self.matcher.match(env, pair(form.rest, None), md)
        return md

    def expand(self, env, md):
        return self.template.expand(md, [])[0]

    ########################################
    # Pattern compiling
    ########################################
    def compile_pattern(self, pattern):
        """\
        Compile pattern into a matcher.
        """
        if not isinstance(pattern, pair):
            raise SyntaxError("Invalid pattern for macro: %s" % pattern)
        # skip the first element, it should be the macro keyword or underscope
        # NOTE, if some invalid expressions are put here, they will be silently
        # ignored
        pattern = pattern.rest

        return self._compile_pattern(pattern)

    def _compile_pattern(self, pat):
        if isinstance(pat, pair):
            mt = SequenceMatcher()
            while isinstance(pat, pair):
                submt = self._compile_pattern(pat.first)
                mt.add_matcher(submt)
                pat = pat.rest
                if isinstance(pat, pair) and pat.first == sym('...'):
                    submt.ellipsis = True
                    pat = pat.rest
            if pat is not None:
                submt = self._compile_pattern(pat)
                mt.add_matcher(RestMatcher(submt))
            return mt

        if isinstance(pat, sym):
            if pat in self.literals:
                return LiteralMatcher(self.env, pat.name)
            if pat == sym('_'):
                return UnderscopeMatcher()
            if self.variables.get(pat.name) is not None:
                raise SyntaxError("Duplicated variable in macro: %s" % pat)
            self.variables[pat.name] = True
            return VariableMatcher(pat.name)

        return ConstantMatcher(pat)

    ########################################
    # Template compiling
    ########################################
    def compile_template(self, expr):
        if isinstance(expr, pair):
            tmpl = SequenceTemplate()
            while isinstance(expr, pair):
                sub_tmpl = self.compile_template(expr.first)
                expr = expr.rest
                while isinstance(expr, pair) and expr.first == sym('...'):
                    sub_tmpl.nflatten += 1
                    expr = expr.rest
                tmpl.add_tmpl(sub_tmpl)
            if expr is not None:
                sub_tmpl = self.compile_template(expr)
                tmpl.set_tail(sub_tmpl)
            return tmpl
        if isinstance(expr, sym) and self.variables.get(expr.name) is not None:
            return VariableTemplate(expr.name)
        return ConstantTemplate(expr)
            

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
        self.ellipsis = False
        self.name = name

    def class_name(self):
        return "%s%s" % (self.__class__.__name__,
                         self.ellipsis and "*" or "")

    def match(self, env, expr, match_dict):
        """\
        Match against expr and return the remaining expression.
        If can not match, raise MatchError.
        """
        raise MatchError("%s: match not implemented" % self)

    def __str__(self):
        return '<%s name=%s>' % (self.class_name(), self.name)

class LiteralMatcher(Matcher):
    """\
    A LiteralMatcher only matches the symbol with the same lexical binding
    or both has no binding.
    """
    def __init__(self, env, name):
        Matcher.__init__(self, name)
        self.loc = self.get_loc(env, name)

    def match(self, env, expr, match_dict):
        pass

    def get_loc(self, env, name):
        if env is None:
            return None
        return env.lookup_location(name)

class ConstantMatcher(Matcher):
    """\
    Matches any constant.
    """
    def __init__(self, value):
        Matcher.__init__(self, None)
        self.value = value
    def match(self, env, expr, match_dict):
        if self.ellipsis:
            while isinstance(expr, pair) and \
                  expr.first == self.value:
                expr = expr.rest
            return expr
        
        if not isinstance(expr, pair) or \
           expr.first != self.value:
            raise MatchError("%s: can not match %s" % (self, expr))
        return expr.rest
    def __str__(self):
        return "<%s value=%s>" % (self.class_name(), self.value)

class VariableMatcher(Matcher):
    """\
    A variable match any single expression.
    """
    def match(self, env, expr, match_dict):
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
    def match(self, env, expr, match_dict):
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
    def match(self, env, expr, match_dict):
        return self.matcher.match(env, pair(expr, None), match_dict)
    def __str__(self):
        return "<RestMatcher: matcher=%s>" % self.matcher

class SequenceMatcher(Matcher):
    """\
    SequenceMatcher hold a sequence of matchers and matches them in that order.
    """
    def __init__(self):
        Matcher.__init__(self, None)
        self.sequence = []

    def match(self, env, expr, match_dict):
        if self.ellipsis:
            md = EllipsisMatchDict()
            try:
                while isinstance(expr, pair):
                    self.match_sequence(env, expr, md)
                    expr = expr.rest
            except MatchError:
                pass
            # merge data in EllipsisMatchDict into match_dict
            match_dict.update(md)
            return expr
        else:
            if not isinstance(expr, pair):
                raise MatchError("%s: unable to match %s" % (self, expr))
            self.match_sequence(env, expr, match_dict)
            return expr.rest

    def match_sequence(self, env, expr, match_dict):
        expr = expr.first
        for m in self.sequence:
            expr = m.match(env, expr, match_dict)
        if expr is not None:
            # not matched expressions
            raise MatchError("%s: ramaining expressions not matched: %s" % (self, expr))
        

    def add_matcher(self, matcher):
        self.sequence.append(matcher)

    def __str__(self):
        return "<%s sequence=[%s]>" % (self.class_name(),
                                       ', '.join([m.__str__()
                                                  for m in self.sequence]))

########################################
# Template expanding
########################################
class Template(object):
    "The base class for all template."
    def __init__(self):
        self.nflatten = 0
        
    def class_name(self):
        return self.__class__.__name__
    
    def expand(self, md, nflatten=0):
        "Expand the template under match dict md."
        raise SyntaxError("Attempt to expand an abstract template.")

class LiteralTemplate(Template):
    # TODO: implement this
    pass

class ConstantTemplate(Template):
    "Template that will expand to a constant."
    def __init__(self, value):
        Template.__init__(self)
        self.value = value

    def expand(self, md, idx=[]):
        return (self.value, )
    
    def __str__(self):
        return "<%s value=%s>" % (self.class_name(), self.value)


class VariableTemplate(Template):
    "Template that reference to a macro variable."
    def __init__(self, name):
        Template.__init__(self)
        self.name = name

    def expand(self, md, idx=[]):
        val = md.get(self.name, Ellipsis())
        for i in idx:
            val = val[i]
        nflatten = self.nflatten
        val = [val]
        while nflatten > 0:
            val = self.flatten(val)
            nflatten -= 1
        if len(val) > 0 and isinstance(val[0], Ellipsis):
            raise SyntaxError("Ellipsis after variable %s is less than expected." % self.name)
        return val

    def flatten(self, val):
        "Flatten ellipsis."
        res = []
        for x in val:
            if not isinstance(x, Ellipsis):
                raise SyntaxError("Too many ellipsis for variable %s" % self.name)
            res.extend(x)
        return res

    def __str__(self):
        return "<%s name=%s>" % (self.class_name(), self.name)

class SequenceTemplate(Template):
    "Template that aggregate a sequence of sub-templates."
    default_tail = ConstantTemplate(None)
    
    def __init__(self):
        Template.__init__(self)
        self.sequence = []
        self.tail = SequenceTemplate.default_tail

        self.ellipsis_names = []

    def add_tmpl(self, tmpl):
        self.calc_ellipsis_names(tmpl)
        self.sequence.append(tmpl)

    def set_tail(self, tmpl):
        """\
        Set the tail template of the sequence. It is normally
        default to ConstantTemplate(None).
        """
        self.calc_ellipsis_names(tmpl)
        self.tail = tmpl

    def calc_ellipsis_names(self, tmpl):
        if isinstance(tmpl, VariableTemplate):
            self.ellipsis_names.append(tmpl.name)
        elif isinstance(tmpl, SequenceTemplate):
            self.ellipsis_names.extend(tmpl.ellipsis_names)

    def expand(self, md, idx=[]):
        return self.expand_flatten(md, idx, self.nflatten)

    def expand_flatten(self, md, idx, flatten):
        if flatten == 0:
            return self.expand_0(md, idx)
        length = 0
        for name in self.ellipsis_names:
            var = md.get(name, Ellipsis())
            for i in idx:
                var = var[i]
            if not isinstance(var, Ellipsis):
                raise SyntaxError("Too many ellipsis after variable %s" % name)
            if length == 0 or length == len(var):
                length = len(var)
            else:
                raise SyntaxError("Incompatible ellipsis match counts for variable %s" % name)
        if length > 0:
            idx.append(0)
            res = []
            for i in range(length):
                idx[-1] = i
                res.extend(self.expand_flatten(md, idx, flatten-1))
            idx.pop()
            return res
        else:
            return ()

    def expand_0(self, md, idx):
        elems = []
        for tmpl in self.sequence:
            elems.extend(tmpl.expand(md, idx))
        rest = self.tail.expand(md, idx)[0]
        for elem in reversed(elems):
            rest = pair(elem, rest)
        return [rest]
        
    def __str__(self):
        return "<%s sequence=[%s], tail=%s>" % (self.class_name(),
                                                ', '.join([tmpl.__str__()
                                                           for tmpl in self.sequence]),
                                                self.tail)
