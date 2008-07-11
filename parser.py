from symbol import Symbol as sym
from cons import Cons as cons

from errors import ParseError

class Parser(object):
    "A simple recursive descent parser for Scheme."
    sym_quote = sym("quote")
    
    def __init__(self, text, name="__unknown__"):
        self.text = text
        self.name = name
        self.pos = 0
        self.line = 1

    def parse(self):
        "Parse the text and return a sexp."
        try:
            return self.parse_expr()
        except IndexError:
            report_error("Unexpected end of code")

    def parse_expr(self):
        self.skip_all()
        
        ch = self.text[self.pos]
            
        if ch.isdigit() or \
           (ch == '#' and self.text[self.pos+1] != '('):
            return self.parse_number()
        if ch == '(':
            return self.parse_list()
        if ch == '\'':
            return self.parse_quote()
        return self.parse_symbol()


    def parse_number(self):
        exactness = None
        radix = 10
        if self.text[self.pos] == '#':
            exactness, radix = self.parse_number_prefix(self)
        num1 = self.parse_number_real(radix)
        return num1
    
    def parse_number_prefix(self):
        "Parse number prefix"
        exactness = None
        radix = 10
        while self.eat('#'):
            ch = self.text[self.pos]
            if ch == 'i':
                exactness = False
            elif ch == 'e':
                exactness = True
            elif ch == 'b':
                radix = 2
            elif ch == 'o':
                radix = 8
            elif ch == 'd':
                radix = 10
            elif ch == 'x':
                radix = 16
            else:
                report_error("Bad number format, unknown radix: %s" % ch)
            self.pos += 1
        return exactness, radix

    def parse_number_real(self, radix):
        "Parse a real number."
        negative = False
        if self.eat('-'):
            negative = True
        self.eat('+')

        pos1 = self.pos
        while self.text[self.pos].isdigit():
            self.pos += 1
        return int(self.text[pos1:self.pos])

    def parse_list(self):
        self.eat('(')
        elems = []
        while self.pos < len(self.text):
            self.skip_all()
            if self.eat(')'):
                elems.append(None)
                break
            if self.eat('.'):
                elems.append(self.parse_expr())
                self.skip_all()
                if not self.eat(')'):
                    self.report_error("Expecting %s, but got %s" %
                                      (')', self.text[self.pos]))
                break
            elems.append(self.parse_expr())
        car = elems.pop()
        for x in reversed(elems):
            car = cons(x, car)
        return car

    def parse_quote(self):
        self.eat('\'')
        return cons(Parser.sym_quote,
                    cons(self.parse_expr(), None))

    def parse_symbol(self):
        pos1 = self.pos
        self.pos += 1
        while self.pos < len(self.text) and \
              not self.text[self.pos].isspace() and \
              not self.text[self.pos] in ['\'', ')', '(', ',', '@', '.']:
            self.pos += 1
        pos2 = self.pos
        return sym(self.text[pos1:pos2])

    def skip_all(self):
        "Skip all non-relevant characters."
        self.skip_ws()
        self.skip_comment()
        self.skip_ws()

    def skip_ws(self):
        "Skip whitespace."
        while self.pos < len(self.text):
            if self.eat('\n'):
                self.line += 1
            elif self.text[self.pos].isspace():
                self.pos += 1
            else:
                break

    def skip_comment(self):
        "Skip comment."
        while self.pos < len(self.text) and \
              self.eat(';'):
            while self.pos < len(self.text) and \
                  self.text[self.pos] != '\n':
                self.pos += 1
            if self.pos < len(self.text):
                self.pos += 1
                self.line += 1
            else:
                break
            
    def eat(self, char):
        if self.text[self.pos] != char:
            return False
        self.pos += 1
        return True
        
    def report_error(self, msg):
        raise ParseError("%s:%d %s" % (self.name, self.line, msg))
