#!/usr/bin/env python
#
# Interfaces For Objects.
# file           : Interface.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-08
# last modified  : 2011-07-27

from Logger import BaseLogger


class Loggable(object):

    log = BaseLogger()
    def openLog(self, filename):
        pass
    def open_log(self, Logger):
        """New interface for logger
        Takes a reference to a logfile and attaches the object.
        """
        pass
    def passCommandToLogger(self, command):
        """DEPRECATED --will be removed in a future revision!
        Allows extermal objects to take control of a logfile,
        with some sane options for dropping calls
        """
        barred = ['open', 'write', 'buffer']
        if command in barred or command[0] == '_':
            return False
        return True

class UpdateListener(object):
    def update(self, *args, **kwargs):
        pass

class UpdateBroadcaster(object):
    _listeners=[]

    def register(self, listener):
        if not listener in self._listeners:
            self._listeners.append(listener)

    def remove(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def broadcast(self, **kwargs):
        map(lambda x:x.update(**kwargs), self._listeners)
