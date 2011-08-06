#!/usr/bin/env python
#
# Visualizer Tests.
# file           : visualizer_test.py
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

    class TestVisualization(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logs/vis_test.log')
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


        def tearDown(self):
            self.memory.reset()
            self.logger.buffer(">-----tearDown")
            self.logger.flush()
            del self.vis

        def test_initialization(self):
            self.logger.buffer(">-----test_initialization")
            self.vis = Visualizer.Visualizer(self.monitor)
            self.vis.add_representation_from_data('processor_cycles')
            self.vis.initialize(name="Test Initialization")
            self.assertEquals(True, True)

        def test_monitor_source_update(self):
            self.logger.buffer(">-----test_monitor_source_update")

            self.vis = Visualizer.Visualizer(self.monitor)
            self.vis.add_representation_from_data("processor_cycles",
                                                  opacity=1.0,
                                                  colour='magenta')
            self.vis.initialize(name="Test Monitor Source Update")
            cycles=100
            for i in range(cycles):
                self.cpu.cycle()
                self.vis.render()
            self.assertEquals(True, True) # Whatever. It gets here, it's fine.

        def test_multiple_representations(self):
            self.logger.buffer(">-----test_monitor_source_update")

            self.vis = Visualizer.Visualizer(self.monitor)
            self.vis.add_representation_from_data("processor_cycles",
                                                  opacity=1.0,
                                                  position=[0.0, 0.1, 0],
                                                  colour='red')
            self.vis.add_representation_from_data("processor_cycles",
                                                  opacity=1.0,
                                                  position=[-0.1, -0.1, 0],
                                                  colour='yellow')
            self.vis.add_representation_from_data("processor_cycles",
                                                  opacity=1.0,
                                                  position=[0.1, -0.1, 0],
                                                  colour='blue')
            self.vis.initialize(name="Test Multiple Representations")

            cycles=100
            for i in range(cycles):
                self.cpu.cycle()
                self.vis.render()
            self.assertEquals(True, True) # Whatever. It gets here, it's fine.

    tests = unittest.TestLoader().loadTestsFromTestCase(TestVisualization)
    unittest.TextTestRunner(verbosity=1).run(tests)
