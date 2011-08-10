#!/usr/bin/env python
#
# Interfaces For Objects.
# file           : Interface.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-08
# last modified  : 2011-07-27

from Logger  import BaseLogger

class LoggerClient(object):
    log = BaseLogger()
    _log = log
    def open_log(self, Logger):
        pass

class UpdateListener(object):
    def update(self, *args, **kwargs):
        pass

class UpdateBroadcaster(object):
    def register(self, listeners, listener):
        """Registers an observer."""
        if not listener in listeners:
            listeners.append(listener)

    def remove(self, listeners, listener):
        """De-registers an observer."""
        if listener in listeners:
            listeners.remove(listener)

    def broadcast(self, listeners, **kwargs):
        """Broadcasts updates to all observers."""
        for listener in listeners:
            listener.update(**kwargs)
