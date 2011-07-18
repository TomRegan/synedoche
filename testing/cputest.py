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

if __name__ == '__main__':

    class TestCpu(unittest.TestCase):

        def setUp(self):
            self.logger=Logger.Logger('cputest.log')
            self.logger.buffer('>-----setUp')
            machine_conf='../../xml/machine.xml'
            instruction_conf='../../xml/instructions.xml'

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

            self.memory=System.Memory(machine_address_space, self.instructions)
            self.memory.openLog(self.logger)

            for segment in machine_memory:
                start = machine_memory[segment][0]
                end   = machine_memory[segment][1]
                self.memory.addSegment(segment, start, end)

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

            self.cpu = Cpu.Cpu(registers=self.registers,
                               memory=self.memory,
                               api=self.api,
                               instructions=self.instructions)
            self.cpu.openLog(self.logger)

        def tearDown(self):
            self.memory.dumpMemory()
            self.logger.buffer('>-----tearDown')
            self.logger.flush()

        def testNoop(self):
            self.logger.buffer('>-----testNoop/Fetch')
            pc=self.cpu._registers.getValue(33)
            cycles=1
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles, self.cpu._registers.getValue(33))
            self.assertEquals([[0]], self.cpu._pipeline)

        def testDecode(self):
            self.logger.buffer('>-----testDecode')
            pc=self.cpu._registers.getValue(33)
            cycles=2
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles, self.cpu._registers.getValue(33))
            self.assertEquals([[0],[0,'j','nop']], self.cpu._pipeline)

        def testExecute(self):
            self.logger.buffer('>-----testExecute')
            pc=self.cpu._registers.getValue(33)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(pc+cycles, self.cpu._registers.getValue(33))
            self.assertEquals([[0],[0,'j','nop'],[0,'j','nop'],[0,'j','nop']], self.cpu._pipeline)

        def testPipeline(self):
            self.logger.buffer('>-----testPipeline')
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals([0,0,0,0], self.cpu.getPipeline())

        def testAddInstruction(self):
            self.logger.buffer('>-----testAddInstruction')
            pc=self.cpu._registers.getValue(33)
            i=self.interpreter.readLine('addi $s0, $zero, 32')
            i=self.interpreter.convert(i)
            self.memory.loadText(i)
            cycles=4
            for i in range(cycles):
                self.cpu.cycle()
            self.assertEquals(32, self.registers.getValue(16))

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCpu)
    unittest.TextTestRunner(verbosity=2).run(tests)
