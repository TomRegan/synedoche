#!/usr/bin/env python
#
# Processor Tests.
# file           : cpu_test.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-10
# last modified  : 2011-08-19
#     2011-08-19 : Added test for breakpoints.

import unittest
import sys
sys.path.append('../')

from module import Api
from module import Builder
from module import Assembler
from module import Logger
from module import Monitor
from module import Processor

from module.System import SigTrap

from module.lib.Functions import binary as bin

if __name__ == '__main__':

    class TestCpu(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logs/cpu_test.log')
            self.monitor=Monitor.Monitor()
            self.logger.buffer('>-----setUp')
            config='../config/mips32/'

            coordinator = Builder.Coordinator()

            coordinator.set_builder(Builder.InstructionBuilder())
            coordinator.make(filename=config)
            self.instructions = coordinator.get_object()

            coordinator.set_builder(Builder.RegisterBuilder(log=self.logger))
            coordinator.make(filename=config)
            self.registers = coordinator.get_object()

            coordinator.set_builder(Builder.MemoryBuilder(log=self.logger))
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

        def test_noop(self):
            self.logger.buffer('>-----testNoop/Fetch')
            pc=self.cpu._registers.get_value(33)
            cycles=1
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.get_value(33))
            self.assertEquals([[0, 'j', 'nop']], self.cpu._pipeline)

        def test_decode(self):
            self.logger.buffer('>-----testDecode')
            pc=self.cpu._registers.get_value(33)
            cycles=2
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.get_value(33))
            self.assertEquals([[0, 'j', 'nop'],
                               [0,'j','nop',{'im':
                                              '00000000000000000000000000',
                                              'op': '000000'}]],
                              self.cpu._pipeline)

        def test_execute(self):
            self.logger.buffer('>-----testExecute')
            pc=self.cpu._registers.get_value(33)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.get_value(33))
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

        def test_pipeline(self):
            self.logger.buffer('>-----testPipeline')
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals([0,0,0,0], self.cpu.get_pipeline())

        def test_add_instruction(self):
            """add instruction works as expected"""
            self.logger.buffer('>-----testAddInstruction')
            i=self.assembler.read_lines(['addi $s0, $zero, 32'])
            i=self.assembler.convert(i)
            self.memory.load_text(i)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(32, self.registers.get_value(16))

        def test_set_on_less_instruction(self):
            """slt instruction works as expected"""
            self.logger.buffer('>-----testSltInstruction')
            i=self.assembler.read_lines(['addi $s1, $zero, 255\n',
                                           'addi $s2, $zero, 1023\n',
                                           'slt  $s0, $s1, $s2'])
            i=self.assembler.convert(i)
            self.memory.load_text(i)
            cycles = 6
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(1, self.registers.get_value(16))

        def test_get_pc_value(self):
            """get_pc_value() returns pc value."""
            self.assertEquals(4194304, self.cpu.get_pc_value())
            self.cpu.cycle()
            self.assertEquals(4194308, self.cpu.get_pc_value())

        def test_break_point(self):
            """Adds a break point and checks for SigTrap."""
            i=self.assembler.read_lines(['addi $s1, $zero, 255\n',
                                           'addi $s2, $zero, 1023\n',
                                           'slt  $s0, $s1, $s2'])
            i=self.assembler.convert(i)
            self.memory.load_text(i)
            self.cpu.add_break_point(int('0x40000c', 16))
            cycles = 100
            with self.assertRaises(SigTrap):
                for i in range(cycles):
                    self.cpu.cycle()
            # Shouldn't get anywhere near 100 cycles.
            self.assertEquals(True, (i < 50))
            # We should have fetched the slt instruction.
            self.assertEquals("00000010001100101000000000101010",
                              bin(self.cpu.get_pipeline()[0], 32)[2:])

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCpu)
    unittest.TextTestRunner(verbosity=1).run(tests)
