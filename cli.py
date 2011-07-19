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
from lib.Evaluator  import Evaluator

class Cli(UpdateListener):
    """
    """
    def __init__(self, instructions, machine):
        self.local_DEBUG=2
        self.simulation=None

        try:
            readline.read_history_file('.cli_history')
        except:
            pass

        try:
            self.simulation=Simulation(instruction_conf=instructions,
                                       machine_conf=machine,
                                       logfile='logs/cli.log')

            self.simulation.connect(self)
            self.size = self.simulation.getInstructionSize()
        except Exception, e:
            self.exception_handler(e)

        try:
            self.run()
        except KeyboardInterrupt, e:
            print '^C'
            self.exit()
        except EOFError, e:
            print '^D'
            self.exit()
        except Exception, e:
            self.exception_handler(e)




    def run(self):
        print "Command Line Client ({:})\nType `help' for more information.".format(VERSION)
        while True:
            line = raw_input('>>> ')
            if len(line) > 0:
                self.parse(line)

    def update(self, *args, **kwargs):
        self.registers = kwargs['registers']
        self.memory    = kwargs['memory']
        self.pipeline  = kwargs['pipeline']

    def step(self):
        self.simulation.step(self)

    def cycle(self):
        self.simulation.cycle(self)


    def parse(self, line):
        """line:str -> ...

        Reads a line of input, executing any commands recognized.

        Raises:
            Exception.
            Exceptions from other frames must be handled.
        """
        line=line.split()
        if line[0][:2] == 'pr':
            try:
                if len(line) > 1:
                    if line[1][:3] == 'reg':
                        if len(line) > 2:
                            self.print_register(*line[2:])
                        else:
                            self.print_registers()
                    elif line[1][:4] == 'pipe':
                        self.print_pipeline()
                    elif line[1][:3] == 'mem':
                        if len(line) > 2:
                            self.print_memory(end=line[2])
                        else:
                            self.print_memory()
                else:
                    self.usage(fun='print')
            except:
                print 'Simulation has not started'
        elif line[0][:4] == 'rese':
            self.reset()
        elif line[0] == 'step':
            self.step()
        elif line[0][:4] == 'cycl':
            self.cycle()
        elif line[0] == 'load':
            if len(line) > 1:
                self.load(line[1])
            else: print "Please supply a filename to read"
        elif line[0][:4] == 'eval':
            try:
                evaluator = Evaluator(simulation=self.simulation,
                                      client=self)
                evaluator.eval()
            except Exception, e:
                name=e.__class__.__name__.replace('_',' ')
                print "{:}: `{:}'".format(name,e.message)

        elif line[0] == 'help':
            self.help()
        elif line[0][:4] == 'vers':
            print VERSION
        elif line[0] == '__except__':
            raise Exception('Intentionally raised exception in {:}'.format(self.__class__.__name__))
        elif line[0] == 'quit' or line[0] == 'exit' or line[0] == '\e':
            self.exit()
        else:
            self.usage(fun=' '.join(line))

    def load(self, filename):
        try:
            self.simulation.load(filename, self)
        except IOError, e:
            sys.stderr.write("No such file: `{:}'\n".format(filename))
        except Exception, e:
            self.exception_handler(e)

    def reset(self):
        self.simulation.reset(self)

    def print_registers(self):
        """Formats and outputs a display of the registers"""
        r=self.registers
        try:
            print "{:-<80}".format('--Registers')
            for i in r.values():
                if i>0 and i % 4 == 0:
                    print ''
                name = self.registers.get_number_name_mappings()[i]
                print("{:>4}({:0>2}):{:.>10}"
                      .format(name[:4],
                      i,
                      hex(r.values()[i])[2:].replace('L', '')),
            print "\n{:-<80}".format('')
        except:
            pass

    def print_register(self, *args):
        """Formats and outputs display of a single register"""
        base = 'd'
        if not args[0].isdigit():
            number = int(args[0][:-1])
            value = self.registers.getValue(number)
            base = args[0][-1:]
        else:
            number = int(args[0])
            value = self.registers.getValue(number)
        name = self.registers.get_number_name_mappings()[number]
        print "{:}({:}):".format(name, number),
        if len(args) > 1:
            base = args[1]
        if base =='d':
            print "{:}".format(value)
        if base =='x':
            print "{:}".format(hex(value)[2:])
        if base =='b':
            print "{:}".format(bin(value, self.size)[2:])

    def print_pipeline(self):
        """Formats and outputs a display of the pipeline"""
        #the if block is just a hack to make exceptions more consistant
        if self.pipeline:
            print "{:-<80}".format('--Pipeline')
            for i in range(len(self.pipeline)):
                print "Stage {:}:{:}".format(i+1,bin(int(self.pipeline[i]),self.size)[2:])
            print "{:-<80}".format('')

    def print_memory(self, **kwargs):
        try:
            end=int(kwargs['end'])
        except:
            end=None
        #print self.memory.get_slice()
        memory_slice = self.memory.get_slice(end=end).items()
        print "{:-<80}".format('--Memory')
        for address, value in sorted(memory_slice, reverse=True):
            print " {:>8}: {:}".format(hex(address)[2:],bin(value,self.size)[2:])
        print "{:-<80}".format('')

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
        if callable(self.simulation):
            self.simulation.disconnect(self)
        sys.exit(args[0])

    def exception_handler(self, e):
        if DEBUG and self.local_DEBUG >= 2:
            traceback.print_exc(file=sys.stderr)
        try: print "Exception: {:}".format(e)
        except:pass
        if DEBUG and self.local_DEBUG >= 1:
            print 'Type: ' + e.__class__.__name__
        self.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        Cli(sys.argv[1], sys.argv[2])
    else:
        sys.stderr.write('Usage: cli <instruction config> <machine config>\n')
