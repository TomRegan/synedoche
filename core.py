#!/usr/bin/env python
#
# core wraps all of the system's modules and libraries,
# performing initialization and providing an interface
# that will be used to run simulations.
# Modules which interface with the system should use core.
# file           : core.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-08
# last modified  : 2011-07-27


import sys
#import traceback
#import os

from module import Api
from module import Builder
from module import Interface
from module import Interpreter
from module import Logger
from module import Monitor
from module import Processor

from datetime import datetime
# used for the TestListener
from module.lib.Functions import hexadecimal as hex

class Simulation(object):
    def __init__(self,
                 config,
                 logfile='logs/core.log'):
        """
        Raises:
            All exceptions must be caught by the client.
        """

        try:
            self._cycles  = 0
            self._clients = []
            self._daemons = []
            self.logfile  = logfile
            self.monitor  = Monitor.Monitor()
            self.logger   = Logger.Logger(self.logfile)

        # We need a logger object that will co-ordinate logging,
        # as well as a connection to the logfile
            self.log = Logger.SystemLogger(self.logger)
            now = datetime.isoformat(datetime.now(), sep = ' ')
            self.log.buffer('system started at {0}'.format(now))
        except Exception as e:
            sys.stderr.write('fatal: failed doing basic init\n{:}\n'
                             .format(e.message))
            raise e

        coordinator = Builder.Coordinator()

        coordinator.set_builder(Builder.InstructionBuilder())
        coordinator.make(filename=config)
        self.instructions = coordinator.get_object()
        self.instruction_size = self.instructions.getSize()

        coordinator.set_builder(Builder.RegisterBuilder())
        coordinator.make(filename=config)
        self.registers = coordinator.get_object()
        self.registers.open_log(self.logger)
        self.registers.open_monitor(self.monitor)

        coordinator.set_builder(Builder.MemoryBuilder())
        coordinator.make(filename=config)
        self.memory = coordinator.get_object()
        self.memory.open_log(self.logger)
        self.memory.open_monitor(self.monitor)

        coordinator.set_builder(Builder.PipelineBuilder())
        coordinator.make(filename=config)
        pipeline = coordinator.get_object()

        del coordinator

        self.api = Api.Sunray()
        self.api.open_log(self.logger)

        self.interpreter = Interpreter.Interpreter(
            instructions=self.instructions, registers=self.registers,
            memory=self.memory)
        self.interpreter.open_log(self.logger)

        self.cpu = Processor.Pipelined(
            registers=self.registers, memory=self.memory,
            api=self.api, instructions=self.instructions,
            pipeline=pipeline)
        self.cpu.open_log(self.logger)
        self.cpu.open_monitor(self.monitor)

        self.log.buffer('initialized with no incidents')
        self.log.flush()

    def __call__(self):
        # Clients need core to be callable
        pass

#
# Control Functions
#
    def run(self, client):
        """Run for a long time."""
        counter = 0
        try:
            while counter < 1000000:
                if counter % 500 == 0 and counter > 0:
                    sys.stderr.write("."),
                self.cycle(client)
                counter = counter + 1
        except KeyboardInterrupt, e:
            print("")
            return
        except Exception, e:
            sys.stderr.write("\n")
            raise e

    def cycle(self, client):
        """Performs one simulation cycle."""
        if not self._authorized_client(client):
            self.log.buffer("blocked `cycle' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        self.log.buffer("`cycle' called by `{0}'"
                        .format(client.__class__.__name__))
        self.cpu.cycle()
        self._cycles = self._cycles + 1

    def step(self, client):
        """Completes [the remainder of] one instruction execution"""
        if not self._authorized_client(client):
            self.log.buffer("blocked `cycle' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        self.log.buffer("`step' called by `{0}'"
                        .format(client.__class__.__name__))
        pipeline_length = self.cpu.get_pipeline_length()
        remaining = pipeline_length - (self._cycles % pipeline_length)
        for i in range(remaining):
            self.cpu.cycle()
            self._cycles = self._cycles + 1

    def evaluate(self, lines, connected, client):
        """Processes cycles for one instruction"""
        if not self._authorized_client(client):
            self.log.buffer("blocked `cycle' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        self.log.buffer("`evaluate' called by `{0}'"
                        .format( client.__class__.__name__))
        expression = self.interpreter.read_lines(lines)
        expression = self.interpreter.convert(expression)
        if connected:
            self.cpu.reset()
            # TODO: review this and comment: why no dumping? 2011-08-04
            self.memory.load_text(expression, and_dump=False)
            for i in range(len(expression)+3):
                self.cpu.cycle()
                self._cycles = self._cycles + 1
        self.log.flush()
        return expression

    def load(self, filename, client):
        """Loads an asm programme into the simulation"""
        if not self._authorized_client(client):
            self.log.buffer("blocked `load' call from unauthorized client `{0}'".format(client.__class__.__name__))
            return
        self.log.buffer("`load' called by `{0}'".format(client.__class__.__name__))
        file_object = open(filename, 'r')
        # We will collect assembly binary and offset data, mainly to print.
        (binary, assembly) = self.interpreter.read_file(file_object)
        programme = self.interpreter.convert(binary)
        (chomp, offset) = self.memory.load_text_and_dump(programme)
        return (assembly, binary, offset)

    def reset(self, client):
        """Resets the simulation processor"""
        if not self._authorized_client(client):
            self.log.buffer("blocked `load' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        self.monitor.reset()
        self.cpu.reset()

#
# Authorization
#

    def connect(self, client):
        """Connects a client while ensuring it implements the correct
        interfaces.

        Only authorized clients are allowed to issue instructions.
        This is to protect against exceptions caused by incomplete
        clients.
        """
        if not hasattr(client, 'update'):
            sys.stderr.write("ERROR: failed to connect client `{0}': it does not implement `update'\n"
                             .format(client.__class__.__name__))
            self.log.write("failed to connect client `{0}': it is not an UpdateListener"
                           .format(client.__class__.__name__))
            return
        if client in self._clients:
            self.log.write("failed to connect `{0}': it is already connected"
                           .format(client.__class__.__name__))
            return
        #
        #we want the client to be an UpdateListener to the CPU to
        #receive its state changes.
        #
        self.cpu.register(client)
        self._clients.append(client)
        self.log.write("attached client `{0}'".format(client.__class__.__name__))
        return self

    def disconnect(self, client):
        """Removes a client from the simulation"""
        if client in self._clients:
            self.cpu.remove(client)
            self.log.write('detatched a client')
        self.log.flush()

#
# Accessors
#

    def get_instruction_size(self):
        """Returns instruction_size:int."""
        return self.instruction_size

    def get_monitor(self):
        """Returns a reference to the monitor object."""
        return self.monitor

    def get_processor(self):
        """Returns a reference to the processor object."""
        return self.cpu
#
# Worker functions
#
    def _authorized_client(self, client):
        return client in self._clients

    def _run_daemons(self):
        pass

    def _add_daemon(self, daemon):
        pass

    def _remove_daemon(self, daemon):
        pass

    #def _log_size_check(self):
    #    size = os.path.getsize(self.logfile)
    #    if size > 2**20:
    #        sys.stderr.write('MESSAGE: logfile is becomming large ({0}-Kb).\n'.format(size/1000))


class TestListener(Interface.UpdateListener):
    def __init__(self, simulation):
        self.s = simulation

    def update(self, *args, **kwargs):
        r=kwargs['registers']
        if False == True:
            try:
                print "{:-<80}".format('--Registers')
                for i in r.values():
                    if i>0 and i % 4 == 0:
                        print ''
                    name = self.s.registers.get_number_name_mappings()[i]
                    print("{:>4}({:0>2}):{:.>10}"
                          .format(name[:4],
                                  i,
                                  hex(r.values()[i])[2:].replace('L', ''))),
                print "\n{:-<80}".format('')
            except:
                pass


if __name__ == '__main__':
    s = Simulation(config='config/mips32/')
    tl = TestListener(s)
    s.connect(tl)
    s.load('asm/tests/add.asm', client=tl)
    try:
        for i in range(12):
            s.cycle(client=tl)
        s.log.flush()
        print(s.monitor)
    except:
        print(s.monitor.data)
        s.log.flush()
        #traceback.print_exc(file=sys.stderr)
