from ..types.symbol import Symbol as sym
from ..types.pair   import Pair as pair

from ..errors import ParseError

def parse(text, name="__unknown__"):
    "Parse a piece of text."
    return Parser(text, name).parse()

class Parser(object):
    "A simple recursive descent parser for Scheme."
    sym_quote = sym("quote")
    sym_quasiquote = sym("quasiquote")
    sym_unquote = sym("unquote")
    sym_unquote_slicing = sym("unquote-slicing")
    
    def __init__(self, text, name="__unknown__"):
        self.text = text
        self.name = name
        self.pos = 0
        self.line = 1

    def parse(self):
        "Parse the text and return a sexp."
        expr = self.parse_expr()
        self.skip_all()
        if self.more():
            self.report_error("Expecting end of code, but more code is got")
        return expr


    def parse_expr(self):
        def parse_pound():
            if self.peak(idx=1) == 't':
                self.pop(n=2)
                return True
            if self.peak(idx=1) == 'f':
                self.pop(n=2)
                return False
            if self.peak(idx=1) == '(':
                return self.parse_vector()
        def parse_number_or_symbol():
            if self.isdigit(self.peak(idx=1)):
                return self.parse_number()
            return self.parse_symbol()
            
        mapping = {
            '#' : parse_pound,
            '(' : self.parse_list,
            "'" : self.parse_quote,
            '`' : self.parse_quote,
            ',' : self.parse_unquote,
            '+' : parse_number_or_symbol,
            '-' : parse_number_or_symbol,
            '"' : self.parse_string
            }

        self.skip_all()

        if not self.more():
            raise ParseError("Nothing to be parsed.")
        ch = self.peak()
        routine = mapping.get(ch)
        
        if routine is not None:
            return routine()
        
        if self.isdigit(ch):
            return self.parse_number()
        return self.parse_symbol()


    def parse_number(self):
        sign1 = 1
        if self.eat('-'):
            sign1 = -1
        self.eat('+')

        num1 = self.parse_unum()
        if self.eat('/'):
            num2 = self.parse_unum()
            if num2 is None:
                self.report_error("Invalid number format, expecting denominator")
            num1 = float(num1)/num2
        if self.peak() in ['+', '-']:
            sign2 = 1
            if self.eat('-'):
                sign2 = -1
            self.eat('+')
            num2 = self.parse_unum()
            if num2 is None:
                num2 = 1
            if not self.eat('i'):
                self.report_error("Invalid number format, expecting 'i' for complex")
            if num2 != 0:
                num1 = num1 + sign2*num2*1j

        return sign1*num1

    def parse_unum(self):
        "Parse an unsigned number."
        isfloat = False
        pos1 = self.pos
        while self.isdigit(self.peak()):
            self.pop()
        if self.eat('.'):
            isfloat = True
        while self.isdigit(self.peak()):
            self.pop()
        pos2 = self.pos
        if pos2 == pos1:
            return None
        if isfloat:
            return float(self.text[pos1:pos2])
        else:
            return int(self.text[pos1:pos2])


    def parse_list(self):
        self.eat('(')
        elems = []
        while self.more():
            self.skip_all()
            if self.peak() == ')':
                elems.append(None)
                break
            if self.peak() == '.' and self.peak(idx=1) != '.':
                self.eat('.')
                elems.append(self.parse_expr())
                self.skip_all()
                break
            elems.append(self.parse_expr())
        if not self.eat(')'):
            self.report_error("Expecting right paren ')'.")
        first = elems.pop()
        for x in reversed(elems):
            first = pair(x, first)
        return first

    def parse_quote(self):
        if self.peak() == '\'':
            s = Parser.sym_quote
        else:
            s = Parser.sym_quasiquote
        self.pop()
        return pair(s, pair(self.parse_expr(), None))

    def parse_unquote(self):
        self.eat(',')
        if self.eat('@'):
            return pair(Parser.sym_unquote_slicing,
                        pair(self.parse_expr(), None))
        return pair(Parser.sym_unquote,
                    pair(self.parse_expr(), None))

    def parse_symbol(self):
        pos1 = self.pos
        self.pop()
        while self.more() and \
              not self.isspace(self.peak()) and \
              not self.peak() in ['\'', ')', '(', ',', '@']:
            self.pop()
        pos2 = self.pos
        return sym(self.text[pos1:pos2])

    def parse_string(self):
        mappings = {
            '"':'"',
            '\\':'\\',
            'n':'\n',
            't':'\t'
            }
            
        self.eat('"')
        strings = []
        pos1 = self.pos
        while self.more():
            if self.peak() == '"':
                break
            if self.peak() == '\\':
                self.pop()
                ch = self.peak()
                if ch in mappings:
                    strings.append(self.text[pos1:self.pos-1])
                    strings.append(mappings[ch])
                    self.pop()
                    pos1 = self.pos
            else:
                if self.peak() == '\n':
                    self.line += 1
                self.pop()
        strings.append(self.text[pos1:self.pos])
        if not self.eat('"'):
            report_error("Expecting '\"' to end a string.")
        return ''.join(strings)
                

    def parse_vector(self):
        pass

    def skip_all(self):
        "Skip all non-relevant characters."
        while True:
            self.skip_ws()
            if self.peak() == ';':
                self.skip_comment()
            else:
                break

    def skip_ws(self):
        "Skip whitespace."
        while self.more():
            if self.eat('\n'):
                self.line += 1
            elif self.isspace(self.peak()):
                self.pop()
            else:
                break

    def skip_comment(self):
        "Skip comment."
        while self.eat(';'):
            while self.more() and not self.eat('\n'):
                self.pop()
            self.line += 1

    def pop(self, n=1):
        "Increase self.pos by n."
        self.pos += n

    def more(self):
        "Whether we have more content to parse."
        return self.pos < len(self.text)
            
    def eat(self, char):
        "Try to eat a character."
        if self.peak() != char:
            return False
        self.pos += 1
        return True

    def peak(self, idx=0):
        "Get the character under self.pos + idx."
        if self.pos + idx < len(self.text):
            return self.text[self.pos + idx]
        return None

    def isdigit(self, ch):
        "Test whether ch is a digit."
        return ch is not None and ch.isdigit()

    def isspace(self, ch):
        "Test whether ch is whitespace."
        return ch is not None and ch.isspace()
        
    def report_error(self, msg):
        "Raise a ParserError with msg."
        raise ParseError("%s:%d %s" % (self.name, self.line, msg))
