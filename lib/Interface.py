#!/usr/bin/env python
''' Interface.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-08
description: Provides support to functions using the logger
'''

class Log(object):
    filename=None
    timed=None
    ready=None
    lines=None
    instance=None
    def buffer(self, string):
        pass
    def write(self, string):
        pass
    def flush(self):
        pass

class Logfile(object):
    def open(self, filename, string):
        pass
    def close(self):
        pass
    def writelines(self, string):
        pass
    def write(self, string):
        pass

class Loggable(object):

    log=Log()
    def openLog(self, filename):
        pass
    def passCommandToLogger(self, command):
        """allows extermal objects to take control of a logfile,
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
