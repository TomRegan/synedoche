#!/usr/bin/env python
#
# Visualization Objects.
# file           : Visualizer.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-03
# last modified  : 2011-08-03

from Interface import UpdateListener
#from sys       import getsizeof

class Visualizer(UpdateListener):

    def __init__(self, Monitor):
        self.data={}
        self._monitor = Monitor

    def update(self, *args, **kwargs):
        self.data['registers'].append(kwargs['registers'])

    def add_data_source(self, obj):
        if hasattr(obj, 'register'):
            self.data['registers']=[]
