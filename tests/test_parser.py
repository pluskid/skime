from skime.parser import parse as p

class TestNumber(object):
    def test_integer(self):
        assert p('0') == 0
