#!/usr/bin/env python
#
# Line completion.
# file           : Completer.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-16
# last modified  : 2011-08-16

class Completer(object):
    def __init__(self, vocabulary):
        self.vocab = vocabulary

    def complete(self, text, state):
        results = [x for x in self.vocab if x.startswith(text)] + [None]
        if len(results) == 1:
            from os import listdir
            path = '.'
            results = [x for x in listdir(path) if x.startswith(text)] + [None]
            #print(results)
        return results[state]
