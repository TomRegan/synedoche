#!/usr/bin/env python
#
# Processor Tests.
# file           : cpu_test.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-10
# last modified  : 2011-07-27

import unittest
import sys
sys.path.append('../')

from module import Api
from module import Builder
from module import Interface
from module import Interpreter
from module import Isa
from module import Logger
from module import Memory
from module import Monitor
from module import Processor
from module import Registers
from module.Memory import (AddressingError, AlignmentError,
                           SegmentationFaultException)


if __name__ == '__main__':

    class TestCpu(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logs/cpu_test.log')
            self.monitor=Monitor.Monitor()
            self.logger.buffer('>-----setUp')
            machine_conf='../config/machine.xml'
            instruction_conf='../config/instructions.xml'

            coordinator = Builder.Coordinator()

            coordinator.set_builder(Builder.InstructionBuilder())
            coordinator.make(filename=instruction_conf)
            self.instructions = coordinator.get_object()

            coordinator.set_builder(Builder.RegisterBuilder())
            coordinator.make(filename=machine_conf)
            self.registers = coordinator.get_object()
            self.registers.open_log(self.logger)

            coordinator.set_builder(Builder.MemoryBuilder())
            coordinator.make(filename=machine_conf)
            self.memory = coordinator.get_object()
            self.memory.open_log(self.logger)
            self.memory.open_monitor(self.monitor)

            coordinator.set_builder(Builder.PipelineBuilder())
            coordinator.make(filename=machine_conf)
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

        def tearDown(self):
            self.memory.reset()
            self.logger.buffer('>-----tearDown')
            self.logger.flush()

        def testNoop(self):
            self.logger.buffer('>-----testNoop/Fetch')
            pc=self.cpu._registers.getValue(33)
            cycles=1
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.getValue(33))
            self.assertEquals([[0, 'j', 'nop']], self.cpu._pipeline)

        def testDecode(self):
            self.logger.buffer('>-----testDecode')
            pc=self.cpu._registers.getValue(33)
            cycles=2
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.getValue(33))
            self.assertEquals([[0, 'j', 'nop'],
                               [0,'j','nop',{'im':
                                              '00000000000000000000000000',
                                              'op': '000000'}]],
                              self.cpu._pipeline)

        def testExecute(self):
            self.logger.buffer('>-----testExecute')
            pc=self.cpu._registers.getValue(33)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.getValue(33))
            self.assertEquals([[0, 'j', 'nop'],
                               [0,'j','nop',{'im':
                                              '00000000000000000000000000',
                                              'op': '000000'}],
                               [0,'j','nop',{'im':
                                              '00000000000000000000000000',
                                              'op': '000000'}],
                               [0,'j','nop',{'im':
                                              '00000000000000000000000000',
                                              'op': '000000'}]],
                              self.cpu._pipeline)

        def testPipeline(self):
            self.logger.buffer('>-----testPipeline')
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals([0,0,0,0], self.cpu.get_pipeline())

        def testAddInstruction(self):
            """add instruction works as expected"""
            self.logger.buffer('>-----testAddInstruction')
            pc=self.cpu._registers.getValue(33)
            i=self.interpreter.read_lines(['addi $s0, $zero, 32'])
            i=self.interpreter.convert(i)
            self.memory.load_text(i)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(32, self.registers.getValue(16))

        def testSetOnLessInstruction(self):
            """slt instruction works as expected"""
            self.logger.buffer('>-----testSltInstruction')
            pc=self.cpu._registers.getValue(33)
            i=self.interpreter.read_lines(['addi $s1, $zero, 255\n',
                                           'addi $s2, $zero, 1023\n',
                                           'slt  $s0, $s1, $s2'])
            i=self.interpreter.convert(i)
            self.memory.load_text(i)
            cycles = 6
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(1, self.registers.getValue(16))

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCpu)
    unittest.TextTestRunner(verbosity=1).run(tests)
