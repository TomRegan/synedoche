#!/usr/bin/env python

import unittest
import sys

from lib import Interface
from lib import XmlLoader as Xml
from lib import Logger
from module import Api
from module import Isa
from module import System
from module import Interpreter
from module import Cpu
from module import Memory
from lib.Functions import binary as bin
from module.Memory import (AddressingError, AlignmentError,
                           SegmentationFaultException)



if __name__ == '__main__':

    class TestMemory(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('memtest.log')
            self.logger.buffer('>-----setUp')
            machine_conf='../config/machine.xml'
            instruction_conf='../config/instructions.xml'

            instruction_reader = Xml.InstructionReader(instruction_conf)

            instruction_language          = instruction_reader.getLanguage()
            instruction_size              = instruction_reader.getSize()
            instruction_syntax            = instruction_reader.getSyntax()
            instruction_implementation    = instruction_reader.getImplementation()
            instruction_values            = instruction_reader.getValues()
            instruction_signatures        = instruction_reader.getSignatures()
            instruction_format_mapping    = instruction_reader.getFormatMapping()
            instruction_format_properties = instruction_reader.getFormatProperties()
            instruction_assembly_syntax   = instruction_reader.getAssemblySyntax()

            machine_reader = Xml.MachineReader(machine_conf)

            machine_language          = machine_reader.getLanguage()
            machine_address_space     = machine_reader.getAddressSpace()
            machine_memory            = machine_reader.getMemory()
            machine_registers         = machine_reader.getRegisters()
            machine_register_mappings = machine_reader.getRegisterMappings()

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
                self.instructions.addAssemblySyntax(instruction,
                    instruction_assembly_syntax[instruction])

            self.memory=Memory.Memory(machine_address_space,
                                      self.instructions)
            self.memory.open_log(self.logger)

            for segment in machine_memory:
                start = machine_memory[segment][0]
                end   = machine_memory[segment][1]
                self.memory.add_segment(segment, start, end)

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

            self.api = Api.Sunray()

            self.interpreter = Interpreter.Interpreter(instructions=self.instructions,
                                                       registers=self.registers,
                                                       memory=self.memory)
            self.interpreter.openLog(self.logger)

            self.cpu = Cpu.Pipelined(registers=self.registers,
                                     memory=self.memory,
                                     api=self.api,
                                     instructions=self.instructions)
            self.cpu.openLog(self.logger)

        def tearDown(self):
            self.memory.reset()
            self.logger.buffer('>-----tearDown')
            self.logger.flush()

        def test32BitWordOperation(self):
            """Store and Load a 32-bit word"""
            size=32
            value=1023
            offset=int('0x7ffffffc',16)
            rvalue=self.wordOperationHelper(offset, value, size)
            self.assertEquals(value, rvalue)

        def test16BitWordOperation(self):
            """Store and Load a 16-bit word"""
            size=16
            value=255
            offset=int('0x7ffffffc',16)
            rvalue=self.wordOperationHelper(offset, value, size)
            self.assertEquals(value, rvalue)

        def test8BitWordOperation(self):
            """Store and Load an 8-bit word"""
            size=8
            value=255
            offset=int('0x7ffffffc',16)
            rvalue=self.wordOperationHelper(offset, value, size)
            self.assertEquals(value, rvalue)

        def wordOperationHelper(self, offset, value, size):
            self.logger.buffer('>-----test{:}BitWordOperation'
                              .format(size))
            self.memory.set_word(offset, value, size)
            rvalue = self.memory.get_word(offset, size)
            return rvalue

        def testAlignmentError(self):
            """Storing data other than on word boundary"""
            self.logger.buffer('>-----testAlignmentError')
            offset=int('0x7ffffffc',16)
            self.memory.get_word(offset, 32)
            offset=int('0x7ffffffd',16)
            with self.assertRaises(AlignmentError):
                self.memory.get_word(offset, 32)
            with self.assertRaises(AlignmentError):
                self.memory.get_word(offset, 16)
            offset=int('0x7ffffffe',16)
            self.memory.get_word(offset, 16)

        def testAddressingError(self):
            """Moving data which is smaller than the addressable space"""
            self.logger.buffer('>-----testAddressingError')
            offset=int('0x7ffffff8',16)
            with self.assertRaises(AddressingError):
                self.memory.get_word(offset,4)

            value=255
            with self.assertRaises(AddressingError):
                self.memory.set_word(offset, value, 4)

        def testSegmentationFaultException(self):
            """Storing data at a protected address"""
            self.logger.buffer('>-----testSegmentationFaultException')
            value=1023
            offset=32
            self.memory.set_word(offset, value, 32)
            rvalue=self.memory.get_word(offset, 32)
            self.assertEquals(value, rvalue)
            offset=int('0x80000000',16)
            with self.assertRaises(SegmentationFaultException):
                self.memory.set_word(offset, value, 32)

        def testLoadText(self):
            """Loading a programme into memory"""
            self.logger.buffer('>-----testLoadText')
            programme=[255,1023,2047,4095]
            self.memory.load_text(programme)
            offset=self.memory.get_start('text')
            for i in range(len(programme)):
                value=self.memory.get_word(offset+(i*4), 32)
                self.assertEquals(programme[i], value)


    tests = unittest.TestLoader().loadTestsFromTestCase(TestMemory)
    unittest.TextTestRunner(verbosity=2).run(tests)
