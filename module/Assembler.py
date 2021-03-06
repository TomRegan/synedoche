#!/usr/bin/env python
#coding=iso-8859-15
#
# Convert Assembly to Machine Instructions.
# file           : Assembler.py
# author         : Tom Regan <noreply.tom.regan@gmail.com>
# since          : 2011-07-05
# last modified  : 2011-07-22 (minor revisions; this is stable)
#     2011-08-18 : Support for multi-part instructions added.
#     2011-08-30 : Fixed bug in proprocessor, ....-fit on bad syntax.


import re

from copy      import deepcopy
from Logger    import AssemblerLogger
from Interface import *

from Logger        import level
from lib.Functions import binary as bin
from lib.Functions import hexadecimal as hex
from lib.Functions import integer as int

BAD = 'Bad instruction or syntax'

class BadInstructionOrSyntax(Exception):
    """Signals bad syntax for the instruction just read"""

class DataMissingException(Exception):
    """Signals object initialization without correct data"""

class DataConversionFromUnknownType(Exception):
    """Signals that conversion was attampted on non-binary data"""



class BaseAssembler(LoggerClient):
    def open_log(self, logger):
        self.log = AssemblerLogger(logger)
        self.log.write("created `{0}' assembler".format(self._language),
                       level.INFO)
    def read_lines(self, lines):
        """Read a line or lines of input and return a list of instructions.

        Description:
           [lines:str]:list -> [instructions:str]:list

        Purpose:
            Reads lines of assembly in the form of a list and returns a
            binary listing. Preprocessing and linking is done.

        Restrictions:
            Behaviour is undefined if argument is not of type <str>,
            representing a binary number.

        Exceptions:
            N/A

        Returns:
            A list of binary instructions.
        """
        pass
    def read_file(self, lines):
        """Reads a file and returns a list of instructions.

        Description:
            lines:file ->
                ([instructions:int]:list, [original:str]:list)

        Purpose:
            Opens a read an assembly file to return a binary listing.
            All the necessary preprocessing and linking will be done.

        Restrictions:
            See exceptions.

        Exceptions:
            Exception

        Returns:
            A tuple, element 0 is a list of binary encoded instructions,
            element 1 is the original listing (processed).
        """
        pass
    def convert(self, lines):
        """Converts a list of binary instructions to an integer list.

        Description:
            [lines:str]:list -> [instructions:int]:list

        Purpose:
            Before attempting to load a program that has been through
            the assembler, it should be converted for use in the
            simulation.

        Restrictions:
            Behaviour is undefined if arguments are not of type <str>,
            representing a binary number.

        Exceptions:
            N/A

        Returns:
            A list of integers.
        """
        pass
    def get_jump_table():
        pass

class Assembler(BaseAssembler):
    # TODO: Try and phase out these declarations and rely on the values
    # given in __init__. (2011-08-18)
    _comment_pattern = None # Regex describing comments.
    _label_pattern   = None # Regex describing a lable.
    _label_reference = None # Regex for a label reference.
    _hex_pattern     = None # Regex for hexadecimal numbers.
    _text_offset     = None # Location to load the program.
    _isa_size        = None # Used to calculate instruction length.

    _instruction_syntax={}
    _format_properties={}
    _format_mappings={}
    _registers={}

    def __init__(self, instructions, registers, memory):
        # TODO: Clearer to access the ISA directly, rather than grabbing
        # all its values at once. (2011-08-28)

        # Values derived from ISA
        self._language           = instructions.get_language()
        self._instruction_syntax = instructions.get_syntax()
        self._instruction_values = instructions.get_values()
        self._format_properties  = instructions.get_format_bit_ranges()
        self._format_mappings    = instructions.get_instruction_to_format_map()
        self._comment_pattern    = instructions.get_assembly_syntax()['comment']
        self._label_pattern      = instructions.get_assembly_syntax()['label']
        self._label_reference    = instructions.get_assembly_syntax()['reference']
        self._hex_pattern        = instructions.get_assembly_syntax()['hex']
        self._label_replacements = instructions.get_label_replacements()
        self._isa_size           = instructions.getSize()
        self._registers          = registers.get_register_mappings()

        # Dynamic data
        self._isa = instructions
        self._jump_table   = {}

        # Constants derived from Memory
        self._text_offset  = memory.get_start('text')
        self._word_spacing = memory.get_word_spacing()


#
# Interface
#
    def read_file(self, file_object):
        if type(file_object) == file:
            self.log.buffer("reading file: {0}".format(file_object.name),
                            level.INFO)
            instructions = self._read(file_object.readlines())
            return (instructions, self._program)
        else:
            raise Exception

    def read_lines(self, lines):
        for line in lines:
            self.log.buffer("reading line: {0}"
                            .format(line.replace('\n', '')),
                            level.FINE)
        instruction = self._read(lines)
        return instruction

    def convert(self, lines):
        try:
            for i in range(len(lines)):
                lines[i] = int(lines[i], 2)
        except:
            raise DataConversionFromUnknownType(
                'Tried to convert from unknown type: {0} {1}'
                .format(lines[i], type(lines[i])))
        return lines

    def get_jump_table(self):
        return self._jump_table

#
# Worker functions
#
    def _read(self, lines):
        """[lines:str]:list -> [instructions:str]:list"""
        lines=self._preprocess(lines)
        lines=self._link(lines)
        lines=self._encode(lines)
        return lines

    def _preprocess(self, lines):
        """ [lines:str]:list -> [lines:str]:list

        Takes a list of lines and removes extraneous information
        like comments and whitespace. A jump-table is also built:
        labels in the assembly are indexed and references to them
        will be replaced in the second pass.

        +------------------------------------------------------+
        | Validation                                           |
        +------------------------------------------------------+
        | none                                                 |
        +------------------------------------------------------+
        """

        self.log.buffer("entering preprocessor", level.FINER)
        #remove all newlines from the list
        lines = ''.join(lines)
        try:
            lines = re.split('\n', lines)
        except:
            self.log.buffer("file format is irregular: expecting newlines, got none",
                            level.ERROR)
            pass
        #we don't want comments, blank lines or whitespace
        for i in range(len(lines)):
            lines[i] = re.sub(self._comment_pattern, '' , lines[i])
            lines[i] = re.sub('\s+', ' ', lines[i])
            lines[i] = lines[i].strip()
        lines = [line for line in lines if line != '']

        #we need to further clean the table so labels are always
        #associated with the correct line
        i = 0
        while i < len(lines):
            if re.search(self._label_pattern, lines[i]):
                match = re.search(self._label_pattern, lines[i])
                if match.group(0) == lines[i] and i+1 < len(lines):
                    #grab the next line to concaternate
                    cat = lines.pop(i+1)
                    lines[i] = lines[i] + ' ' + cat
                    i = i+1
            i = i+1

        # Here we will build a table mapping labels to memory locations.
        self._jump_table.clear()


        try:
            # FIX: This code might me dicey. Throws a key exception on
            # very malformed input. Why? (2011-08-30)
            # Not a big problem, only affects syntax errors.
            offset = 0
            for i in range(len(lines)):
                # Here we look for a label.
                if re.search(self._label_pattern, lines[i]):
                    match = re.search(self._label_pattern, lines[i])
                    # Here we define the reference for this label.
                    # This will be its lookup name in the table.
                    reference = re.search(self._label_reference, match.group())
                    self._jump_table[reference.group(1)] = offset
                    self.log.buffer("mapped label `{0}' to {1}"
                                    .format(reference.group(1), offset),
                                    level.FINER)
                    # Finally, remove labels from the original
                    lines[i] = re.sub(self._label_pattern,'',lines[i])

                # We will calculate any aditional offset required in the case
                # of multi-part instructions.
                instruction  = lines[i].split()[0]
                format_name  = self._format_mappings[instruction]
                fetch_cycles = self._isa.get_format_cycles()[format_name]
                offset = offset + fetch_cycles

                # We don't want unnecessary whitespace
                lines[i] = lines[i].strip()
                self.log.buffer("processed  {0}".format(lines[i]), level.FINE)
        except:
                raise BadInstructionOrSyntax(
                    "{:} on line {:}:\n{:}"
                    .format(BAD, i+1, lines[i]))

        lines = [line for line in lines if line != '']
        self.log.buffer("leaving preprocessor", level.FINER)
        return lines

    def _link(self, lines):
        """Transforms the program replacing branch identifiers with
        computed addresses that reference labels in the code.

        Description:
            [lines:str]:list -> [lines:str]:list
            Ensures all branch identifiers are valid (ie. corresponding
            labels were found in preprocessing) and replaces them with
            interim hexadecimal addresses. These hex addresses will be
            replaced during encoding with binary values.

        Purpose:
            preprocessing -> [linking] -> encoding

        Restrictions:
            N/A

        Exceptions:
            N/A

        Returns:
            A version of the program having all labels replaced with memory
            references.
         """

        # TODO: Linker needs to handle absolute addresses in multi-part
        # instructions. (2011-08-28)
        self.log.buffer("entering linker", level.FINER)

        # We will store the return data in output.
        output=[]
        for i in range(len(lines)):
            # First, check the instruction is valid. If we try to operate
            # with badly formed instructions at this point we will raise
            # an exception in the re module.
            instruction = lines[i].split()[0]
            if instruction in self._format_mappings:
                syntax     = self._instruction_syntax[instruction]
                expression = '^' + syntax['expression'] + '$'
            else:
                raise BadInstructionOrSyntax(
                    "{:} on line {:}:\n{:}"
                    .format(BAD, i+1, lines[i]))

            # We should have this data from the previous stage, or have
            # thrown an error.
            match = re.search(expression, lines[i])
            if match:
                key = re.match('\w+', lines[i]).group()
                if key in self._label_replacements:
                    group = self._label_replacements[key][1]
                    mode  = self._label_replacements[key][2]

                    pattern = self._instruction_syntax[key]['expression']
                    match = re.search(pattern, lines[i])
                    label = match.group(group)

                    # Calculate either absolute or relative addresses based on
                    # configuration file/API options.
                    try:
                        if mode == 'absolute':
                            base = self._text_offset
                            offset = self._jump_table[label]
                            offset = hex(base + (offset * self._word_spacing),
                                         self._isa_size/4)
                        elif mode == 'relative':
                            offset = str(self._jump_table[label] - i)
                    # Finally, we can replace the label.
                        lines[i] = lines[i].replace(label, offset)
                        self.log.buffer("replaced identifier `{:}'"
                                        "with {:}".format(
                                        label, offset), level.FINER)
                    except:
                        raise BadInstructionOrSyntax(
                            "{:} on line {:}: Label not found.\n{:}"
                            .format(BAD, i+1, lines[i]))
                output.append(lines[i])
            else:
                raise BadInstructionOrSyntax(
                    "{:} on line {:}:\n{:}"
                    .format(BAD, i+1, lines[i]))

        self._program = deepcopy(output)
        self.log.buffer("leaving linker", level.FINER)
        return output

    def _encode(self, lines):
        """Takes a list of assembly instructions (with decoded identifiers)
        and returns a list of binary machine instructions.

        Description:
            [lines:str]:list -> [lines:str]:list

            Once an assembly program has been through the linker and all
            the identifiers (label references) have been replaced with
            numerical values, the encoder can convert the instruction
            to binary using instruction and format data from the config.

        Purpose:
            Encodes assembly instructions as binary: the final step in
            converting an assembly program into machine code.

            Encoding gurantees that instruction syntax is correct and
            that identifiers and register references are valid.

        Restrictions:
            The result of processing identifiers which have not been
            converter is undefined.

        Exceptions:
            Raises:
                BadInstructionOrSyntax

        Returns:
            A list of binary manchine instructions.
        """

        self.log.buffer("entering encoder", level.FINER)
        # We will return output and use instruction_fields to build up
        # each instruction.
        output             = []
        instruction_fields = {}
        for line in lines:
            #
            # Here we will read the instruction on each line, try to fetch
            # a regular expression for it, and split it into groups.
            #
            instruction = line.split()[0]
            if instruction in self._format_mappings:
                syntax     = self._instruction_syntax[instruction]
                expression = '^' + syntax['expression'] + '$'
                self.log.buffer("matching `{0}' instruction"
                                .format(instruction), level.FINER)
                match = re.search(expression, line)
                if match:
                    # Here we are looping over fields in the instruction
                    # format and determining their values.
                    for i in range(len(match.groups())):
                        field = syntax['symbols'][i][0]
                        value = match.groups()[i]

                        # This block deals with the possibility that the
                        # symbol is a hex number.
                        if value not in self._registers:
                            try:
                                if value[:2] == '0x':
                                    value = int(value, 16)
                                elif value.endswith(self._hex_pattern):
                                    value = value.replace(self._hex_pattern, '')
                                    value = int(value, 16)
                                else:
                                    value=int(value)
                            except:
                                line = "`" + line + "'"
                                raise BadInstructionOrSyntax(
                                    "{:} on line {:}:Non-ref or digit.\n{:}"
                                    .format(BAD, i+1, lines[i]))
                        # We have identified the field. Log it...
                        self.log.buffer("`{0}' is {1}"
                                        .format(field, value), level.FINEST)
                        # ...and add it to the instruction.
                        instruction_fields[field] = value

                    # This block adds the preset field values.
                    values = self._instruction_values[instruction]
                    for field in values:
                        instruction_fields[field] = values[field]
                        self.log.buffer("`{0}' is {1}"
                                        .format(field, values[field]),
                                        level.FINEST)

                    #print("instruction: {:}".format(instruction_fields))


                    # Here we binary-encode the instruction.
                    format_name = self._format_mappings[instruction]
                    fetch_cycles = self._isa.get_format_cycles()[format_name]
                    instruction_length = self._isa_size * fetch_cycles
                    # Creates a list of 0s which we can edit to match the
                    # instruction.
                    instruction_raw = instruction_length * '0'.split()
                    for field in instruction_fields:
                        start = self._format_properties[format_name][field][0]
                        end   = self._format_properties[format_name][field][1]+1
                        # If the value is a register reference, encode the
                        # register number, otherwise encode literal.
                        if instruction_fields[field] in self._registers:
                            value = self._registers[instruction_fields[field]]
                        else:
                            value = instruction_fields[field]
                        # Now insert the encoded field into the instruction.
                        width = end - start
                        value = bin(value, size = width)[2:]
                        instruction_raw[start:end] = value
                        self.log.buffer("{:}:{:} is {:}"
                                        .format(start, end, value),
                                        level.FINEST)

                    # Finally convert the instruction from a list to a string.
                    instruction_raw = "".join(instruction_raw)
                    # Bon.
                    self.log.buffer("encoded {0}".format(instruction_raw),
                                    level.FINER)

                    # Split the instruction if it spans multiple words.
                    # eg. 8085 Direct Addressing uses three 8 bit parts
                    # despite being an 8 bit ISA.
                    self.log.buffer("splitting into {:}-bit chunks"
                                    .format(self._isa_size),
                                    level.FINER)
                    start = 0
                    end   = 1
                    for i in range(len(instruction_raw)):
                        if end % self._isa_size == 0:
                            part = instruction_raw[start:end]
                            # Log entry is indented for readability.
                            self.log.buffer(
                                "  split {:}".format(part),
                             level.FINER)
                            output.append(part)
                            start = end
                        end = end + 1
                    #output.append(instruction_raw)
                else:
                    raise BadInstructionOrSyntax(
                        "{:} on line {:}:\n{:}"
                        .format(BAD, i+1, lines[i]))
            # TODO: Keep this block under review. Probably kept for a reason.
            #(2011-08-18)
            #elif instruction in self._special_instructions:
                #
                #we aren't dealing with specials yet
                #this will probably come into play with assembler directives
                #
                #output.append(instruction)
                #pass
            else:
                raise BadInstructionOrSyntax(
                    "{:} on line {:}:\n{:}"
                    .format(BAD, i+1, lines[i]))
            instruction_fields.clear()
        self.log.buffer("leaving encoder", level.FINER)
        return output
