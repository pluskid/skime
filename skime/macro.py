from .pair   import Pair as pair
from .symbol import Symbol as sym

class Macro(object):
    def __init__(self, body):
        if not isinstance(body, pair):
            pass
