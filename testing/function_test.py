#!/usr/bin/env python
#
# Helper Function Tests.
# file           : function_test.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-24
# last modified  : 2011-07-27

import unittest
import sys
sys.path.append('../')

from module.lib.Functions import binary as bin
from module.lib.Functions import integer as int

if __name__ == '__main__':

    class TestHelperFunctions(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_signed_int(self):
            """lib.functions.binary extends sign correctly"""
            a = bin(-4, 8)[2:]
            b = bin(4, 8)[2:]
            self.assertEquals('11111100', a)
            self.assertEquals('00000100', b)
            c = int(a, 2, signed=True)
            d = int(b, 2, signed=True)
            self.assertEquals(-4, c)
            self.assertEquals(4, d)

    tests = unittest.TestLoader().loadTestsFromTestCase(TestHelperFunctions)
    unittest.TextTestRunner(verbosity=1).run(tests)
