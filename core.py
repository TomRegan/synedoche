#!/usr/bin/env python
''' core.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-08
description: core wraps all of the system's modules and libraries,
             performing initialization and providing an interface
             that will be used to run simulations.

             Modules which interface with the system should use core.
'''

import sys
import traceback
import os

from lib import Interface
from lib import XmlLoader as Xml
from lib import Logger
from module import Cpu
from module import Api
from module import Isa
from module import Memory
from module import System
from module import Interpreter
from datetime import datetime
from lib.Functions import binary as bin
from lib.Functions import hexadecimal as hex

#TODO
#as a nicity, builders for initialization
#

class Simulation(object):
    def __init__(self,
                 machine_conf,
                 instruction_conf,
                 logfile='logs/core.log'):
        """
        Raises:
            All exceptions must be caught by the client.
        """

        #
        #we need a logger object that will co-ordinate logging,
        #as well as a connection to the logfile
        #
        try:
            self._cycles =0
            self._clients=[]
            self._daemons=[]
            self.logfile=logfile
            self.logger = Logger.Logger(self.logfile)
            self.log = Logger.SystemLogger(self.logger)
            now = datetime.isoformat(datetime.now(), sep=' ')
            self.log.buffer('system started at {0}'.format(now))
        except Exception as e:
            sys.stderr.write('fatal: failed doing basic init\n')
            raise e
        #self.logSizeCheck()

        #
        #we need values from the instruction config file
        #
        try:
            instruction_reader = Xml.InstructionReader(instruction_conf)

            instruction_language          = instruction_reader.getLanguage()
            instruction_size              = instruction_reader.getSize()
            instruction_syntax            = instruction_reader.getSyntax()
            instruction_implementation    = instruction_reader.getImplementation()
            instruction_values            = instruction_reader.getValues()
            instruction_signatures        = instruction_reader.getSignatures()
            instruction_format_mapping    = instruction_reader.getFormatMapping()
            instruction_format_properties = instruction_reader.getFormatProperties()
            instruction_assembly_syntax   = instruction_reader.get_assembler_syntax()

            self.instruction_size         = instruction_size
        except Exception as e:
            sys.stderr.write('fatal: failed trying to read instructions config\n')
            raise e

        #
        #we also need values from the machine configuration file
        #
        try:
            machine_reader = Xml.MachineReader(machine_conf)

            machine_language          = machine_reader.getLanguage()
            machine_address_space     = machine_reader.getAddressSpace()
            machine_memory            = machine_reader.getMemory()
            machine_registers         = machine_reader.getRegisters()
            machine_register_mappings = machine_reader.getRegisterMappings()
        except Exception as e:
            sys.stderr.write('fatal: failed trying to read machine config\n')
            raise e

        #
        #we need to build an instruction set object
        #
        try:
            self.instructions=Isa.InstructionSet(instruction_language,
                                                 instruction_size)

            for instruction in instruction_syntax:
                self.instructions.addSyntax(instruction,
                    instruction_syntax[instruction])

            for instruction in instruction_implementation:
                self.instructions.addImplementation(instruction,
                    instruction_implementation[instruction])

            for instruction in instruction_values:
                self.instructions.addValue(instruction,
                    instruction_values[instruction])

            for instruction in instruction_signatures:
                signature={}
                for field in instruction_signatures[instruction]:
                    value=instruction_values[instruction][field]
                    signature[field]=value
                self.instructions.addSignature(instruction, signature)

            for instruction in instruction_format_mapping:
                self.instructions.addFormatMapping(instruction,
                    instruction_format_mapping[instruction])

            for instruction in instruction_format_properties:
                self.instructions.addFormatProperty(instruction,
                    instruction_format_properties[instruction])

            for instruction in instruction_assembly_syntax:
                self.instructions.addAssemblySyntax(instruction[0],
                                                    instruction[1])
        except Exception as e:
            sys.stderr.write('fatal: failed trying to initialize isa\n')
            raise e

        #
        #we need a memory object for the CPU
        #
        try:
            self.memory=Memory.Memory(machine_address_space, self.instructions)
            self.memory.open_log(self.logger)

            for segment in machine_memory:
                start = machine_memory[segment][0]
                end   = machine_memory[segment][1]
                self.memory.add_segment(segment, start, end)
        except Exception as e:
            sys.stderr.write('fatal: failed trying to initialize memory\n')
            raise e


        #
        #registers for the CPU
        #
        try:
            self.registers=System.Registers()

            for register in machine_registers:
                privilege = machine_registers[register]['privilege']
                profile   = machine_registers[register]['profile']
                value     = machine_registers[register]['value']
                size      = machine_registers[register]['size']
                self.registers.addRegister(number=register,
                                           value=value,
                                           size=size,
                                           profile=profile,
                                           privilege=privilege)

            for register in machine_register_mappings:
                self.registers.addRegisterMapping(register,
                    machine_register_mappings[register])

        except Exception as e:
            sys.stderr.write('fatal: died trying to initialize registers\n')
            raise e

        #
        #we need an api object for the CPU
        #
        try:
            self.api = Api.Sunray()
            self.api.openLog(self.logger)
        except Exception as e:
            sys.stderr.write('fatal: died trying to initialize api\n')
            raise e

        #
        #and an interpreter object
        #
        try:
            self.interpreter = Interpreter.Interpreter(instructions=self.instructions,
                                                       registers=self.registers,
                                                       memory=self.memory)
            self.interpreter.open_log(self.logger)
        except Exception as e:
            sys.stderr.write('fatal: died trying to initialize interpreter\n')
            raise e

        #
        #finally, the CPU
        #
        self.cpu = Cpu.Pipelined(registers=self.registers,
                                 memory=self.memory,
                                 api=self.api,
                                 instructions=self.instructions)
        self.cpu.open_log(self.logger)

        self.log.buffer('initialized with no incidents')
        self.log.flush()

    def __call__(self):
        """Clients need core to be callable"""
        pass

    #
    #core interface is below
    #
    #def log_size_check(self):
    #    size = os.path.getsize(self.logfile)
    #    if size > 2**20:
    #        sys.stderr.write('MESSAGE: logfile is becomming large ({0}-Kb).\n'.format(size/1000))

    def _authorized_client(self, client):
        return client in self._clients

    def cycle(self, client):
        """Performs one simulation cycle."""
        if not self._authorized_client(client):
            self.log.buffer("blocked `cycle' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        self.log.buffer("`cycle' called by `{0}'".format(client.__class__.__name__))
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
        remaining = 4 - (self._cycles % 4)
        for i in range(remaining):
            self.cpu.cycle()
            self._cycles = self._cycles + 1

    def complete(self, client):
        pass

    def evaluate(self, lines, connected, client):
        """Processes cycles for one instruction"""
        #assert type(lines) == list
        if not self._authorized_client(client):
            self.log.buffer("blocked `cycle' call from unauthorized client `{0}'"
                            .format(client.__class__.__name__))
            return
        #
        #this will be changed when we start loading necessary data from
        #config
        #
        self.log.buffer("`evaluate' called by `{0}'"
                        .format( client.__class__.__name__))
        expression = self.interpreter.read_lines(lines)
        expression = self.interpreter.convert(expression)
        if connected:
            self.cpu.reset()
            self.memory.load_text(expression, and_dump=False)
            #self.step(client)
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
        programme = self.interpreter.read_file(file_object)
        programme = self.interpreter.convert(programme)
        self.memory.load_text_and_dump(programme)

    def reset(self, client):
        """Resets the simulation processor"""
        if not self._authorized_client(client):
            self.log.buffer("blocked `load' call from unauthorized client `{0}'".format(client.__class__.__name__))
            return
        self.cpu.reset()

    def connect(self, client):
        """Connects a client while ensuring it implements the correct
        interfaces.

        Only authorized clients are allowed to issue instructions.
        This is to protect against exceptions caused by incomplete
        clients.
        """
        if not isinstance(client, Interface.UpdateListener):
            sys.stderr.write("ERROR: failed to connect client `{0}': it is not an UpdateListener\n".format(client.__class__.__name__))
            self.log.write("failed to connect client `{0}': it is not an UpdateListener".format(client.__class__.__name__))
            return
        if client in self._clients:
            self.log.write("failed to connect `{0}': it is already connected".format(client.__class__.__name__))
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

    def runDaemons(self):
        pass

    def addDaemon(self, daemon):
        pass

    def removeDaemon(self, daemon):
        pass

    def getInstructionSize(self):
        """-> instruction_size:int"""
        return self.instruction_size

class TestListener(Interface.UpdateListener):
    def __init__(self, simulation):
        self.s = simulation

    def update(self, *args, **kwargs):
        r=kwargs['registers']
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
    try:
        s = Simulation(machine_conf='config/machine.xml',
                       instruction_conf='config/instructions.xml')
        tl = TestListener(s)
        s.connect(tl)
        #s.connect(tl)
        s.load('asm/add.asm', client=tl)
        for i in range(8):
            s.cycle(client=tl)
        s.log.flush()
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        try: print "Exception: " + e.message
        except: pass
        try: print "Exception: " + e.message
        except: pass
