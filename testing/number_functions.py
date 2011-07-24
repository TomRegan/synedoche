#!/usr/bin/env python
#
# Helper Function Unit Tests.
# file           : number_functions.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-24
# last modified  : 2011-07-24

import unittest
import sys
sys.path.append('../')

from lib.Functions import binary as bin
from lib.Functions import integer as int

if __name__ == '__main__':

    class TestHelperFunctions(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def testSignExtension(self):
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
    unittest.TextTestRunner(verbosity=2).run(tests)
