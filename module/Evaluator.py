#!/usr/bin/env python
#
# Line Evaluator.
# file           : Evaluator.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-18
# last modified  : 2011-08-17
#     2011-08-17 : Changes in cli (size field removed)

# FIX: SigTerm causes fatal error. (2011-08-18)


from lib.Functions import binary as bin

class Evaluator(object):
    def __init__(self, simulation, client):
        self.simulation   = simulation
        self.client       = client
        self.size         = client.isize
        self.connected    = True
        self.display_eval = True

    def eval(self):
        """A line-mode evaluator used for running assembly instructions.

        Raises:
            EOFError (routine to signal end)
        """
        lines=[]

        breaking = False
        i=1
        while True:
            try:
                if not breaking:
                    char = "% "
                else:
                    char = ". "
                line=raw_input(char)
                line=line.strip()
                if len(line) > 1:
                    i = i + 1
                    breaking = False
                    if line[:1] == '\\':
                        self.eval_leader(line[1:])
                    elif line in ['end']:
                        self.evaluate(lines)
                        break
                    elif line[:3] == 'del':
                        drop = int(line[3:])
                        if drop < len(lines):
                            lines.pop(drop)
                            print 'Dropped line {:}'.format(drop)
                        else:
                            print 'No such line: {:}'.format(drop)
                    else:
                        lines.append(line+'\n')
                else:
                    if breaking:
                        self.evaluate(lines)
                        break
                    breaking = True
            except EOFError, e:
                print '\e'
                self.evaluate(lines)
                break

    def evaluate(self, lines):
        expression = self.simulation.evaluate(lines, self.connected,
                                              self.client)
        if self.display_eval:
            for line in expression:
                print bin(int(line),self.size)[2:]

    def eval_leader(self, line):
        line.strip()
        if line == 'e':
            raise EOFError
        elif line == 'l':
            print 'syntax: [on|off|toggle] bool_prop [property]'
            print 'connected    [toggle] ({:})'.format(str(self.connected))
            print 'display_eval [toggle] ({:})'.format(str(self.display_eval))
        elif line == 'c':
            self.eval_toggle('connected')
        elif line == 'd':
            self.eval_toggle('display_eval')

    def eval_toggle(self, arg):
        if arg == 'connected':
            if self.connected:
                print 'Disconnected'
                self.connected=False
            else:
                print 'Connected'
                self.connected=True
        if arg == 'display_eval':
            if self.display_eval:
                print 'Evaluation off'
                self.display_eval=False
            else:
                print 'Evaluation on'
                self.display_eval=True
