#!/usr/bin/env python
#
# Statistical Data Monitoring.
# file           : Monitor.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-27
# last modified  : 2011-07-27

class BaseMonitor(object):
    """Provides storage for statistical data."""

    def __init__(self):
        self.data = {}

    def get_int_prop(self):
        """Returns a value from the integers table"""
        pass

    def get_bool_prop(self):
        """Returns a value from the booleans table"""
        pass

    def set_int_prop(self, key, value):
        """Sets a value in the integers table"""
        pass

    def set_bool_prop(self, key, value):
        """Sets a value in the booleans table"""
        pass

    def increment(self, key, increment=None):
        """Increments an integer value"""
        pass

    def decrement(self, key, deincrement=None):
        """Decrements an integer value"""
        pass

    def toggle(self, key):
        """Toggles a boolean value on/off"""
        pass


class Monitor(BaseMonitor):

    def __init__(self):
        self.data = {'int_prop':{}, 'bool_prop':{}}

    def __getattr__(self, name):
        if name == 'int_prop':
            return self.get_int_prop()
        elif name == 'bool_prop':
            return self.get_bool_prop()
        else:
            raise AttributeError

    def __setitem__(self, key, value):
        if type(value) == int:
            self.set_int_prop(key, value)
        elif type(value) == bool:
            self.set_bool_prop(key, value)

    def get_int_prop(self, key=None):
        """Returns a stored integer property."""
        if key != None:
            try:
                return self.data['int_prop'][key]
            except:
                0
            return 0
            #return self.data['int_prop']

    def get_bool_prop(self, key=None):
        """Returns a stored boolean property."""
        if key != None:
            try:
                return self.data['bool_prop'][key]
            except:
                return False
            return self.data['bool_prop']

    def set_int_prop(self, key, value):
        """Stores an integer property."""
        self.data['int_prop'][key] = value

    def set_bool_prop(self, key, value):
        """Stores an boolean property."""
        self.data['bool_prop'][key] = value

    def increment(self, key, increment=1):
        """Increments a stored integer property."""
        if key in self.data['int_prop']:
            self.data['int_prop'][key] = self.get_int_prop(key) + increment
        else:
            self.data['int_prop'][key] = increment

    def decrement(self, key, decrement=1):
        """Decrements a stored integer property."""
        if key in self.data['int_prop']:
            self.data['int_prop'][key] = self.get_int_prop(key) - decrement
        else:
            self.data['int_prop'][key] = -decrement

    def toggle(self, key):
        """Toggles a stored boolean property."""
        if key in self.data['bool_prop']:
            self.data['bool_prop'][key] = (not self.data['bool_prop'][key])
        else:
            self.data['bool_prop'][key] = True
