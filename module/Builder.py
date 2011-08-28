#!/usr/bin/env python
#
# Builder.
# file           : Builder.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-22
# last modified  : 2011-08-03

from module import XmlParser
from module import Isa
from module import Registers
from module import Memory

class Coordinator(object):
    def __init__(self):
        self._builder = None

    def make(self, **args):
        if not self._builder == None:
            self._builder.make(**args)

    def set_builder(self, builder):
        self._builder = builder

    def get_object(self):
        return self._builder.obj

class Builder(object):
    def __init__(self, log=None):
        self.obj = None
        self.logger = log

    def make(self):
        pass

class InstructionBuilder(Builder):
    def make(self, **args):
        config = args['filename']

        self.obj = Isa.Isa()

        reader = XmlParser.InstructionReader(config)
        instruction_language     = reader.data['language']
        instruction_size         = reader.data['size']
        # We're not currently using this data. It can links the config
        # to a specific api implementation.
        instruction_api          = reader.data['api']
        instruction_formats      = reader.data['formats']
        instruction_instructions = reader.data['instructions']
        instruction_assembler    = reader.data['assembler']
        del reader

        self.obj.set_global_language(instruction_language)
        self.obj.set_global_size(instruction_size)
        self.obj.set_global_api(instruction_api)
        self.obj.add_assembler_syntax(instruction_assembler)
        for instruction in instruction_instructions:
            self.obj.add_mapping(
                instruction[0], instruction[1])
            self.obj.add_instruction_signature(
                instruction[0], instruction[2], instruction[4])
            self.obj.add_instruction_syntax(
                instruction[0], instruction[3], instruction[5])
            self.obj.add_instruction_preset(
                instruction[0], instruction[4])
            self.obj.add_instruction_implementation(
                instruction[0], instruction[6])
            self.obj.add_instruction_replacement(
                instruction[0], instruction[7])

        for instruction_format in instruction_formats:
            self.obj.add_format_property_bit_ranges(
                instruction_format[0], instruction_format[2])
            self.obj.add_format_property_size(
                instruction_format[0], instruction_format[1])
            self.obj.add_format_property_cycles(
                instruction_format[0], instruction_format[3])

class RegisterBuilder(Builder):
    def make(self, **args):
        config = args['filename']

        self.obj=Registers.Registers()
        if self.logger != None:
            self.obj.open_log(self.logger)

        reader = XmlParser.MachineReader(config)
        machine_registers = reader.data['registers']
        del reader

        for register in machine_registers:
            number  = register[1]
            size    = register[2]
            write   = register[3]
            profile = register[4]
            value   = register[6]
            self.obj.add_register(number=number,
                                 value=value,
                                 size=size,
                                 profile=profile,
                                 privilege=write)
            self.obj.add_register_mapping(
                register[0], register[1])

class MemoryBuilder(Builder):
    def make (self, **args):
        config = args['filename']

        reader = XmlParser.MachineReader(config)
        machine_memory = reader.data['memory']
        del reader

        data = machine_memory[0:3]
        self.obj=Memory.Memory(data)
        if self.logger != None:
            self.obj.open_log(self.logger)

        segments = machine_memory[3:]
        for segment in segments:
            name  = segment[0]
            start = segment[1]
            end   = segment[2]
            self.obj.add_segment(name, start, end)

class PipelineBuilder(Builder):
    def make(self, **args):
        config = args['filename']

        reader = XmlParser.MachineReader(config)
        self.obj = reader.data['pipeline']
        del reader
