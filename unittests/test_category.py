from category import *
import unittest

class TestCategory():
    def testMatch(self):
        path = '/CATEGORY/CLASS/instance/PROTOCOL/METHOD'
        target = {'category': 'CATEGORY',
            'class': 'CLASS',
            'file': None,
            'dir': 'instance',
            'protocol': 'PROTOCOL',
            'method': 'METHOD'}
        assert CategoryPathParser(0).match(path) == target
