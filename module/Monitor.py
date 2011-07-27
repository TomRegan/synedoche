#!/usr/bin/env python
#
# Statistical Data Monitoring.
# file           : Monitor.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-27
# last modified  : 2011-07-27

class BaseMonitor(object):
    """Provides storage for statistical data."""
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

    def increment(self, key, increment):
        """Increments an integer value"""
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
        if key != None:
            return self.data['int_prop'][key]
        try:
            return self.data['int_prop']
        except:
            0

    def get_bool_prop(self, key=None):
        if key != None:
            return self.data['bool_prop'][key]
        try:
            return self.data['bool_prop']
        except:
            return False

    def set_int_prop(self, key, value):
        self.data['int_prop'][key] = value

    def set_bool_prop(self, key, value):
        self.data['bool_prop'][key] = value

    def increment(self, key, increment=1):
        self.data['int_prop'][key] = self.data['int_prop'][key] + increment

    def toggle(self, key):
        self.data['bool_prop'][key] = (not self.data['bool_prop'][key])
