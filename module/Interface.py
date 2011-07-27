#!/usr/bin/env python
#
# Interfaces For Objects.
# file           : Interface.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-08
# last modified  : 2011-07-27

from Logger  import BaseLogger
from Monitor import BaseMonitor


class Loggable(object):

    log = BaseLogger()
    _log = log
    def open_log(self, Logger):
        pass

class MonitorNode(object):
    mon = BaseMonitor()
    _mon = mon
    def open_monitor(self, Monitor):
        pass

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
