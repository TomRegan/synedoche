#!/usr/bin/env python
''' cli.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-15
description: A CLI client for the system.
'''

import sys
import readline

from core import *
from lib.Header import *
from lib.Functions import binary as bin
from lib.Exceptions import *
from lib.Interface  import UpdateListener

class Cli(UpdateListener):
    """
    """
    def __init__(self, instructions, machine):
        self.local_DEBUG=1
        try:
            readline.read_history_file('.cli_history')
        except:
            pass

        self.simulation=Simulation(instruction_conf=instructions,
                                   machine_conf=machine,
                                   logfile='logs/cli.log')

        self.simulation.connect(self)
        self.size = self.simulation.getInstructionSize()

        try:
            self.run()
        except KeyboardInterrupt, e:
            print '^C'
            self.exit()
        except EOFError, e:
            print '^D'
            self.exit()
        except Exception, e:
            if DEBUG and self.local_DEBUG >= 2:
                traceback.print_exc(file=sys.stderr)
            try: print "Exception: " + e.message
            except:
                try: print "Exception: " + e.message
                except: pass
            if DEBUG and self.local_DEBUG >= 1:
                print 'Exception type: ' + e.__class__.__name__
            self.exit(1)


    def run(self):
        print "Command Line Client ({:})\nType `help' for more information.".format(VERSION)
        while True:
            line = raw_input('>>> ')
            if len(line) > 0:
                self.parse(line)

    def eval(self):
        lines=[]
        class EvalProperties(object):
            connected=True
            display_eval=False
        local_props = EvalProperties()

        while True:
            try:
                line=raw_input('% ')
                line=line.strip()
                if line[:1] == '\\':
                    self.eval_leader(line[1:], local_props)
                elif line in ['end']:
                    self.eval_leader('e', local_props)
                elif line[:3] == 'del':
                    drop = int(line[3:])
                    if drop < len(lines):
                        lines.pop(drop)
                        print 'Dropped line {:}'.format(drop)
                    else:
                        print 'No such line: {:}'.format(drop)
                else:
                    lines.append(line+'\n')
            except EOFError, e:
                print '\e'
                expression = self.simulation.evaluate(lines, local_props.connected, self)
                if local_props.display_eval:
                    for line in expression:
                        print bin(int(line),self.size)[2:]
                break

    def eval_leader(self, line, local):
        line.strip()
        if line == 'e':
            raise EOFError
        elif line == 'l':
            print 'syntax: [on|off|toggle] bool_prop [property]'
            print 'connected    [toggle] ({:})'.format(str(local.connected))
            print 'display_eval [toggle] ({:})'.format(str(local.display_eval))
        elif line == 'c':
            self.eval_toggle('connected')
        elif line == 'd':
            self.eval_toggle('display_eval')

    def eval_toggle(self, arg, local):
        if arg == 'connected':
            if local.connected:
                print 'Disconnected'
                local.connected=False
            else:
                print 'Connected'
                local.connected=True
        if arg == 'display_eval':
            if local.display_eval:
                print 'Evaluation off'
                local.display_eval=False
            else:
                print 'Evaluation on'
                local.display_eval=True

    def parse(self, line):
        """line:str -> ...

        Reads a line of input, executing any commands recognized.

        Raises:
            Exception.
            Exceptions from other frames must be handled.
        """
        line=line.split()
        if line[0] == 'except':
            raise Exception
        if line[0][:2] == 'pr':
            try:
                if len(line) > 1:
                    if line[1][:3] == 'reg':
                        if len(line) > 2:
                            self.print_register(int(line[2]))
                        else:
                            self.print_registers()
                    elif line[1][:2] == 'pi':
                        self.print_pipeline()
                    elif line[1][:3] == 'mem':
                        if len(line) > 2:
                            self.print_memory(end=line[2])
                        self.print_memory()
                else:
                    self.usage(fun='print')
            except:
                print 'Simulation has not started'
        elif line[0][:2] == 'ev':
            self.eval()
        elif line[0] == 'help':
            self.help()
        elif line[0] == 'version':
            print VERSION
        elif line[0] == 'quit' or line[0] == 'exit' or line[0] == '\e':
            self.exit()
        else:
            self.usage(fun=' '.join(line))

    def print_registers(self):
        """Formats and outputs a display of the registers"""
        r=self.registers
        try:
            print "{:-<80}".format('--Registers')
            for i in r.values():
                if i>0 and i % 5 == 0:
                    print ''
                print "{:>2}:{:.>10}".format(hex(i)[2:],hex(r.values()[i])[2:]),
            print "\n{:-<80}".format('')
        except:
            pass

    def print_register(self, number):
        """Formats and outputs display of a single register"""
        value = self.registers.getValue(number)
        print "Base10: {:}, Base2: {:}, Base16: {:}".format(value,bin(value,self.size)[2:],hex(value))

    def print_pipeline(self):
        """Formats and outputs a display of the pipeline"""
        #the if block is just a hack to make exceptions more consistant
        if self.pipeline:
            print "{:-<80}".format('--Pipeline')
            for i in range(len(self.pipeline)):
                print "Stage {:}:{:}".format(i+1,bin(int(self.pipeline[i]),self.size)[2:])
            print "{:-<80}".format('')

    def print_memory(self, **kwargs):
        print self.memory.getSlice()

    def update(self, *args, **kwargs):
        self.registers = kwargs['registers']
        self.memory    = kwargs['memory']
        self.pipeline  = kwargs['pipeline']

    def usage(self, *args, **kwargs):
        usage={'print':'print <register>|<registers>'}
        if kwargs['fun'] in usage:
            print 'Usage: ' + usage[kwargs['fun']]
        else:
            print "Unrecognized function: `{:}'. Try `help'".format(kwargs['fun'])

    def help(self):
        print 'help will go here'

    def exit(self, *args, **kwargs):
        if len(args) < 1:
            args=[0]
            print "Bye!"
        readline.write_history_file('.cli_history')
        self.simulation.disconnect(self)
        sys.exit(args[0])

if __name__ == '__main__':
    if len(sys.argv) > 2:
        Cli(sys.argv[1], sys.argv[2])
    else:
        sys.stderr.write('Usage: cli <instruction config> <machine config>\n')
