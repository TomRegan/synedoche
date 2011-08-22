#!/usr/bin/env python
#
# Memory Tests.
# file           : memory_test.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-10
# last modified  : 2011-07-27


import unittest
import sys
sys.path.append('../')

from module import Api
from module import Builder
from module import Logger
from module import Assembler
from module import Monitor
from module import Processor
from module.Memory import (AddressingError, AlignmentError,
                           SegmentationFaultException)



if __name__ == '__main__':

    class TestMemory(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logs/mem_test.log')
            self.monitor=Monitor.Monitor()
            self.logger.buffer('>-----setUp')
            config='../config/mips32/'

            coordinator = Builder.Coordinator()

            coordinator.set_builder(Builder.InstructionBuilder())
            coordinator.make(filename=config)
            self.instructions = coordinator.get_object()

            coordinator.set_builder(Builder.RegisterBuilder())
            coordinator.make(filename=config)
            self.registers = coordinator.get_object()
            self.registers.open_log(self.logger)

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

            self.assembler = Assembler.Assembler(
                instructions=self.instructions, registers=self.registers,
                memory=self.memory)
            self.assembler.open_log(self.logger)

            self.cpu = Processor.Pipelined(
                registers=self.registers, memory=self.memory,
                api=self.api, instructions=self.instructions,
                pipeline=pipeline[0],
                flags=pipeline[1])
            self.cpu.open_log(self.logger)

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
            """Storing data other than on word boundary raises exception"""
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
            """Moving data which is smaller than the addressable space
            raises exeption
            """
            self.logger.buffer('>-----testAddressingError')
            offset=int('0x7ffffff8',16)
            with self.assertRaises(AddressingError):
                self.memory.get_word(offset,4)

            value=255
            with self.assertRaises(AddressingError):
                self.memory.set_word(offset, value, 4)

        def testSegmentationFaultException(self):
            """Storing data at a protected address raises exeption"""
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
    unittest.TextTestRunner(verbosity=1).run(tests)
