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
            self.logger=Logger.Logger('LOGcputest.log')
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
            instruction_assembly_syntax   = instruction_reader.get_assembler_syntax()

            machine_reader = Xml.MachineReader(machine_conf)

            machine_language          = machine_reader.getLanguage()
            memory_data               = machine_reader.get_memory()
            machine_registers         = machine_reader.getRegisters()
            machine_register_mappings = machine_reader.getRegisterMappings()
            machine_pipeline          = machine_reader.get_pipeline()

###########################################################################
###########################################################################

            reader = XmlParser.InstructionReader(instruction_conf)

            instruction_language     = reader.data['language']
            instruction_size         = reader.data['size']
            instruction_api          = reader.data['api']
            instruction_formats      = reader.data['formats']
            instruction_instructions = reader.data['instructions']
            instruction_assembler    = reader.data['assembler']

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
                #self.instructions.add_instruction_replacement(
                #    instruction[0], instruction[7])
            for format in instruction_formats:
                self.instructions.add_format_properties(
                    format[0], format[2])

###########################################################################
###########################################################################

            #self.instructions=Isa.InstructionSet(instruction_language,
            #                                     instruction_size)

            #instruction_language          = instruction_reader.getLanguage()
            #instruction_size              = instruction_reader.getSize()
            #instruction_syntax            = instruction_reader.getSyntax()
            #instruction_implementation    = instruction_reader.getImplementation()
            #instruction_values            = instruction_reader.getValues()
            #instruction_signatures        = instruction_reader.getSignatures()
            #instruction_format_mapping    = instruction_reader.getFormatMapping()
            #instruction_format_properties = instruction_reader.getFormatProperties()
            #instruction_assembly_syntax   = instruction_reader.get_assembler_syntax()

            #for instruction in instruction_syntax:
            #    self.instructions.addSyntax(instruction,
            #        instruction_syntax[instruction])

            #for instruction in instruction_implementation:
            #    self.instructions.addImplementation(instruction,
            #        instruction_implementation[instruction])
            #    #print instruction_implementation[instruction]

            #for instruction in instruction_values:
            #    self.instructions.addValue(instruction,
            #        instruction_values[instruction])

            #for instruction in instruction_signatures:
            #    signature={}
            #    for field in instruction_signatures[instruction]:
            #        value=instruction_values[instruction][field]
            #        signature[field]=value
            #    self.instructions.addSignature(instruction, signature)

            #for instruction in instruction_format_mapping:
            #    self.instructions.addFormatMapping(instruction,
            #        instruction_format_mapping[instruction])

            #for instruction in instruction_format_properties:
            #    self.instructions.addFormatProperty(instruction,
            #        instruction_format_properties[instruction])

            #for instruction in instruction_assembly_syntax:
            #    self.instructions.addAssemblySyntax(instruction[0],
            #                                        instruction[1])

###########################################################################
###########################################################################

            data = memory_data[0:3]
            self.memory=Memory.Memory(self.instructions, data)
            self.memory.open_log(self.logger)

            segments = memory_data[3:]
            for segment in segments:
                name  = segment[0]
                start = segment[1]
                end   = segment[2]
                self.memory.add_segment(name, start, end)

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
