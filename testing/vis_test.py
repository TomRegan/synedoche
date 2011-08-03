#!/usr/bin/env python
#
# Visualizer Tests.
# file           : vis_test.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-08-03
# last modified  : 2011-08-03

import unittest
import sys
sys.path.append('../')

from module import Visualizer
from module import Logger
from module import Monitor
from module import Builder
from module import Api
from module import Processor
from module import Interpreter

if __name__ == '__main__':

    class TestHelperFunctions(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logs/vis_test.log')
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

            self.vis = Visualizer.Visualizer()
            self.vis.add_data_source(self.cpu)

        def tearDown(self):
            self.memory.reset()
            self.logger.buffer('>-----tearDown')
            self.logger.flush()

        def test_initialization(self):
            self.logger.buffer('>-----test_initialization')
            cycles=10
            for i in range(cycles):
                self.cpu.cycle()


    tests = unittest.TestLoader().loadTestsFromTestCase(TestHelperFunctions)
    unittest.TextTestRunner(verbosity=1).run(tests)
