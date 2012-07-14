#!/usr/bin/env python
#
# System functions for the API.
# file           : System.py
# author         : Tom Regan <noreply.tom.regan@gmail.com>
# since          : 2011-07-22
# last modified  : 2011-07-22

class SigTerm(Exception):
    pass
class SigXCpu(Exception):
    pass
class SigTrap(Exception):
    pass
class SigIll(Exception):
    pass
class SigFpe(Exception):
    pass

class SystemCall(object):
    def service(self, number):
        if number == 10:
            raise SigTerm('SIGTERM(10) received')
        if number == 24:
            raise SigXCpu('SIGXCPU(24) received')
        if number == 16435934:
            raise SigTrap('SIGTRAP(16435934) received')
        if number == 16435935:
            raise SigFpe('SIGFPE(16435935) received')
        if number == 16435936:
            raise SigIll('SIGILL(16435936) received')
