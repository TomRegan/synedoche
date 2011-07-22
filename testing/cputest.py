#!/usr/bin/env python

import unittest
import sys

from lib import Interface
from lib import XmlParser
from lib import XmlLoader as Xml
from lib import Logger
from module import Api
from module import Isa
from module import System
from module import Interpreter
from module import Processor
from module import Memory
from module.Memory import (AddressingError, AlignmentError,
                           SegmentationFaultException)


if __name__ == '__main__':

    class TestCpu(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('logcputest.log')
            self.logger.buffer('>-----setUp')
            machine_conf='../config/machine.xml'
            instruction_conf='../config/instructions.xml'

            reader = XmlParser.MachineReader(machine_conf)
            machine_language          = reader.data['language']
            machine_memory            = reader.data['memory']
            machine_registers         = reader.data['registers']
            machine_pipeline          = reader.data['pipeline']
            del reader

            reader = XmlParser.InstructionReader(instruction_conf)
            instruction_language     = reader.data['language']
            instruction_size         = reader.data['size']
            instruction_api          = reader.data['api']
            instruction_formats      = reader.data['formats']
            instruction_instructions = reader.data['instructions']
            instruction_assembler    = reader.data['assembler']
            del reader

            self.instructions=Isa.Isa()

            self.instructions.set_global_language(instruction_language)
            self.instructions.set_global_size(instruction_size)
            self.instructions.add_assembler_syntax(instruction_assembler)
            for instruction in instruction_instructions:
                self.instructions.add_mapping(
                    instruction[0], instruction[1])
                self.instructions.add_instruction_signature(
                    instruction[0], instruction[2], instruction[4])
                self.instructions.add_instruction_syntax(
                    instruction[0], instruction[3], instruction[5])
                self.instructions.add_instruction_preset(
                    instruction[0], instruction[4])
                self.instructions.add_instruction_implementation(
                    instruction[0], instruction[6])
                #TODO
                #integrate instruction replacement!
                #
                self.instructions.add_instruction_replacement(
                    instruction[0], instruction[7])
            for format in instruction_formats:
                self.instructions.add_format_properties(
                    format[0], format[2])

            data = machine_memory[0:3]
            self.memory=Memory.Memory(self.instructions, data)
            self.memory.open_log(self.logger)

            segments = machine_memory[3:]
            for segment in segments:
                name  = segment[0]
                start = segment[1]
                end   = segment[2]
                self.memory.add_segment(name, start, end)

            self.registers=System.Registers()
            self.registers.open_log(self.logger)

            for register in machine_registers:
                number  = register[1]
                size    = register[2]
                write   = register[3]
                profile = register[4]
                value   = register[6]
                self.registers.addRegister(number=number,
                                           value=value,
                                           size=size,
                                           profile=profile,
                                           privilege=write)
                self.registers.addRegisterMapping(
                    register[0], register[1])

            self.api = Api.Sunray()

            self.interpreter = Interpreter.Interpreter(instructions=self.instructions,
                                                       registers=self.registers,
                                                       memory=self.memory)
            self.interpreter.openLog(self.logger)

            self.cpu = Processor.Pipelined(registers=self.registers,
                                           memory=self.memory,
                                           api=self.api,
                                           instructions=self.instructions,
                                           pipeline=machine_pipeline)
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
            self.assertEquals([[0]], self.cpu._pipeline)

        def testDecode(self):
            self.logger.buffer('>-----testDecode')
            pc=self.cpu._registers.getValue(33)
            cycles=2
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.getValue(33))
            self.assertEquals([[0],[0,'j','nop']], self.cpu._pipeline)

        def testExecute(self):
            self.logger.buffer('>-----testExecute')
            pc=self.cpu._registers.getValue(33)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles*4, self.cpu._registers.getValue(33))
            self.assertEquals([[0],[0,'j','nop'],[0,'j','nop'],[0,'j','nop']], self.cpu._pipeline)

        def testPipeline(self):
            self.logger.buffer('>-----testPipeline')
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals([0,0,0,0], self.cpu.get_pipeline())

        def testAddInstruction(self):
            self.logger.buffer('>-----testAddInstruction')
            pc=self.cpu._registers.getValue(33)
            i=self.interpreter.read_lines(['addi $s0, $zero, 32'])
            i=self.interpreter.convert(i)
            self.memory.load_text(i)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(32, self.registers.getValue(16))

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCpu)
    unittest.TextTestRunner(verbosity=2).run(tests)
