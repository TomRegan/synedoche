#!/usr/bin/env python
#
# System functions for the API.
# file           : SystemCall.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-22
# last modified  : 2011-07-22

class SigTerm(Exception):
    pass
class SigTrap(Exception):
    pass

class SystemCall(object):
    def service(self, number):
        if number == 10:
            raise SigTerm('SIGTERM(10) received')
        if number == 16435934:
            raise SigTrap('SIGTRAP(16435934) received')
