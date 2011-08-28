#!/usr/bin/env python
''' ErrorLib.py
author:      Tom Regan <code.tregan@gmail.com>
since:       2011-07-06
description: Home for all the error-types and base error class
'''

class Exception(Exception):

    def __init__(self, message):
        self.message = message

    def what(self):
        return self.message
