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

        if ch.isdigit():
            return self.parse_number()
        if ch == '#':
            if self.text[self.pos+1] == 't':
                return True
            if self.text[self.pos+1] == 'f':
                return False
            if self.text[self.pos+1] == '(':
                return self.parse_vector()
        if ch == '(':
            return self.parse_list()
        if ch == '\'':
            return self.parse_quote()
        if ch in ['+', '-'] and \
           self.pos < len(self.text) and \
           self.text[self.pos].isdigit():
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
                report_error("Invalid number format, expecting denominator")
            num1 = float(num1)/num2
        if self.text[self.pos] in ['+', '-']:
            sign2 = 1
            if self.eat('-'):
                sign2 = -1
            self.eat('+')
            num2 = self.parse_unum()
            if num2 is None:
                num2 = 1
            if not self.eat('i'):
                report_error("Invalid number format, expecting 'i' for complex")
            num1 = num1 + sign2*num2*1j

        return sign1*num1

    def parse_unum(self):
        "Parse an unsigned number."
        isfloat = False
        pos1 = self.pos
        while self.text[self.pos].isdigit():
            self.pos += 1
        if self.eat('.'):
            isfloat = True
        while self.text[self.pos].isdigit():
            self.pos += 1
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

    def parse_vector(self):
        pass

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
