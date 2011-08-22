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
from module import Graphics
from module import Logger
from module import Monitor
from module import Builder
from module import Api
from module import Processor
from module import Assembler

if __name__ == '__main__':

    class TestVisualization(unittest.TestCase):

        def setUp(self):
            self.logger  = Logger.Logger('logs/vis_test.log')
            self.monitor = Monitor.Monitor()
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
            self.cpu.open_monitor(self.monitor)


        def tearDown(self):
            self.memory.reset()
            self.logger.buffer(">-----tearDown")
            self.logger.flush()

        @unittest.skip("module not routinely used")
        def test_visual_initialization(self):
            self.logger.buffer(">-----test_visual_initialization")
            self.vis = Visualizer.Visualizer(self.monitor)
            self.vis.add_representation_from_data('processor_cycles')
            self.vis.initialize(name="Test Initialization")
            self.assertEquals(True, True)

        @unittest.skip("module not routinely used")
        def test_visual_monitor_source_update(self):
            self.logger.buffer(">-----test_visual_monitor_source_update")

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

        @unittest.skip("module not routinely used")
        def test_visual_multiple_representations(self):
            self.logger.buffer(">-----test_visual_multiple_representations")

            self.vis = Visualizer.Visualizer(self.monitor)
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='red')
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='yellow')
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='blue')
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='green')
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='magenta')
            self.vis.add_representation_from_data("processor_cycles",
                                                  colour='cyan')
            self.vis.initialize(name="Test Multiple Representations")

            cycles=100
            for i in range(cycles):
                self.cpu.cycle()
                self.vis.render()
            self.assertEquals(True, True)

        def test_graphics_initialization(self):
            self.logger.buffer(">-----test_graphics_initialization")
            visual = Graphics.Visualizer()
            visual.initialize()
            self.assertEquals(True, True)

        def test_graphics_monitor_source_update(self):
            self.logger.buffer(">-----test_graphics_initialization")
            visual = Graphics.Visualizer()
            visual.update(self.monitor.get_int_prop('processor_cycles'))
            self.assertEquals(True, True)

        def test_graphics_multiple_representations(self):
            counter1 = 8
            counter2 = 6
            counter3 = 4
            counter4 = 3
            counter5 = 5
            counter6 = 7
            visual = Graphics.Visualizer()
            visual.update([counter1, counter2, counter3,
                           counter4, counter5, counter6])
            visual.add_node(0, "Anne")
            visual.add_node(1, "Bob")
            visual.add_node(2, "Carol")
            visual.add_node(3, "David")
            visual.add_node(4, "Eleanor")
            visual.add_node(5, "Fred")
            visual.set_edge_layout_hub()
            visual.set_text_layout_default()
            visual.initialize("Test Multiple Representations")
            for i in range(50):
                visual.update([counter1, counter2, counter3,
                               counter4, counter5, counter6])
                visual.render()
                counter1 = counter1 + 0.1
                if i % 10 == 0:
                    counter4 = counter4 + 1

    tests = unittest.TestLoader().loadTestsFromTestCase(TestVisualization)
    unittest.TextTestRunner(verbosity=1).run(tests)
