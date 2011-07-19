#!/usr/bin/env python
#coding=iso-8859-15
''' Interpreter.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-05
modified:    2011-07-09
description: Module containing the interpreter functions
'''
import re
import lib.Errors as Errors

from lib.Logger     import InterpreterLogger
from lib.Functions  import binary as bin
from lib.Interface  import Loggable

class Bad_instruction_or_syntax(Exception):
    """Signals bad syntax for the instruction just read"""

class DataMissingException(Exception):
    """Signals object initialization without correct data"""

class DataConversionFromUnknownType(Exception):
    """Signals that conversion was attampted on non-binary data"""



class Interpreter(Loggable):

    _comment_pattern=None #regex describing comments
    _label_pattern=None   #regex describing a lable
    _label_reference=None #regex for a label reference
    _jump_table={}        #table of label addresses
    _text_offset=None     #location to load the programme
    _isa_size=None        #used to calculate instruction length

    _instruction_syntax={}
    _format_properties={}
    _format_mappings={}
    _registers={}

    def __init__(self, instructions, registers, memory):
        """Takes a string via read_lines() or a file using readFile()
        containing assembly and returns a list of machine instructions.

        Each stage may do some amount of validation, and exceptions
        may be raised.

        Returns:
            file:object -> [instructions:str]:list
            line:str    -> [instructions:str]:list
        Initialization:
            instructions:object -> modules.Isa.InstructionSet
            registers:object    -> modules.System.Registers
            memory:object       -> modules.System.Memory

        Raises:
            DataMissingException

        Usage:
            try:
                interpreter=Interpreter(instructions, registers, memory)
                programme=interpreter.readFile(file)
            except DataMissingException as e:
                print e.message
            except Bad_instruction_or_syntax as e:
                print e.message
        """
        try:
            self._language               = instructions.getLanguage()
            self._instruction_syntax     = instructions.getSyntax()
            self._instruction_values     = instructions.getValues()
            self._format_properties      = instructions.getFormatProperties()
            self._format_mappings        = instructions.getFormatMapping()
            self._comment_pattern        = instructions.getAssemblySyntax()['comment']
            self._label_pattern          = instructions.getAssemblySyntax()['label']
            self._label_reference        = instructions.getAssemblySyntax()['label_ref']
            self._isa_size               = instructions.getSize()
            self._registers              = registers.getRegisterMappings()
            #
            #WARNING as of 2011-07-19 the great interface change™ is in
            #effect. The following member functions are contradictory
            #and must be set on a per-instance basis.
            #
            self._text_offset            = memory.get_start('text')
            #self._text_offset            = memory.getStart('text')
        except Exception as e:
            raise DataMissingException('Missing data for Interpreter: '+e.message)


    def open_log(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """
        self.log = InterpreterLogger(logger)
        self.log.write("created `{0}' interpreter".format(self._language))

    def read_file(self, file_object):
        """file:object -> [instructions:str]:list

        Usage:
            interpreter.readFile(file)

        Raises:
            Exception
        """
        if type(file_object) == file:
            self.log.buffer("reading file: {0}".format(file_object.name))
            instructions = self._read(file_object.readlines())
            return instructions
        else:
            raise Exception

    def read_lines(self, lines):
        """[lines:str]:list -> [instructions:str]:list

        Usage:
            interpreter.read_lines(str)
        """
        for line in lines:
            self.log.buffer("reading line: {0}".format(line))
        instruction = self._read(lines)
        return instruction

    def convert(self, lines):
        """[lines:str]:list -> [instructions:int]:list

        Before attempting to load a programme that has been through
        the interpreter, it should be converted for use in the
        simulation.
        """
        try:
            for i in range(len(lines)):
                lines[i] = int(lines[i],2)
        except:
            raise DataConversionFromUnknownType('Tried to convert from unknown type: {0} {1}'.format(lines[i], type(lines[i])))
        return lines

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

        self.log.buffer("entering preprocessor")
        #
        #An object lesson in writing comments about _why_ you're doing
        #somethingstill, if it looks stupid but it works, it ain't that
        #stupid.
        #
        lines = ''.join(lines)
        try:
            lines = re.split('\n', lines)
        except:
            self.log.buffer("file format is irregular: expecting newlines, got none")
            pass
        #
        #we don't want comments or blank lines
        #
        for i in range(len(lines)):
            lines[i] = re.sub(self._comment_pattern,'',lines[i])
        lines = [line for line in lines if line != '']
        #
        #we want a table mapping labels to memory locations
        #
        self._jump_table.clear()
        for i in range(len(lines)):
            if re.search(self._label_pattern, lines[i]):
                match = re.search(self._label_pattern, lines[i])
                #we will want to look up the label reference, not the
                #label itself.
                reference = re.search(self._label_reference, match.group())
                self._jump_table[reference.group(1)] = i
                self.log.buffer("mapped label `{0}' to {1}".format(reference.group(1), i))
                #finally, remove labels from the original
                lines[i]=re.sub(self._label_pattern,'',lines[i])
            #we don't want unnecessary whitespace
            lines[i] = lines[i].strip()
            self.log.buffer("processed  {0}".format(lines[i]))
        lines = [line for line in lines if line != '']
        self.log.buffer("leaving preprocessor")
        return lines

    def _link(self, input_):
        """[lines:str]:list -> [lines:str]:list

        Returns a version of the programme with all labels replaced
        by memory references.

        +------------------------------------------------------+
        | Validation                                           |
        +------------------------------------------------------+
        | jump labels are valid, ie. they were found during    |
        | preprocessing                                        |
        +------------------------------------------------------+
        """

        self.log.buffer("entering linker")
        output=[]
        for i in range(len(input_)):
            output.append(input_[i].split())
        for x in range(len(output)):
            for y in range(len(output[x])):
                if output[x][y] in self._jump_table:
                    #
                    #we will return hexadecimal references purely
                    #so that an error raised at this point
                    #can be easilly distinguished
                    #
                    substitute = self._jump_table[output[x][y]]
                    self.log.buffer("mapped `{0}' to {1}".format(output[x][y], substitute))
                    output[x][y] = hex(substitute)
        #
        #programme should be joined as a list of lines
        #
        for i in range(len(output)):
            output[i] = ' '.join(output[i])
        self._jump_table.clear()
        self.log.buffer("leaving linker")
        return output

    def _encode(self, lines):
        """ [lines:str]:list -> [instructions:str]:list

        Returns a list of machine instructions.

        Raises:
            Bad_instruction_or_syntax

        +------------------------------------------------------+
        | Validation                                           |
        +------------------------------------------------------+
        | syntax is valid                                      |
        | register references are valid                        |
        +------------------------------------------------------+
        """

        self.log.buffer("entering encoder")
        base_16 = 16
        base_2  =  2
        base    = base_16
        output=[]
        instruction_fields={}
        for line in lines:
            instruction = line.split()[0]
            #
            #we have to do a lot of checking to make sure
            #there aren't any key errors
            #
            # 1. check the instuction (add,sub..)exists
            # 2. ...has the right syntax (->match)
            # 3. ...references to registers
            # 4. earlier we converted labels into hex, need to be int
            #
            if instruction in self._format_mappings:
                syntax=self._instruction_syntax[instruction]
                expression = '^' + syntax['expression'] + '$'
                self.log.buffer("matching `{0}' instruction".format(instruction))
                if re.search(expression, line):
                    match = re.search(expression, line)
                    #
                    #we want to add the recognisable fields to
                    #the instruction we are building
                    #
                    for i in range(len(match.groups())):
                        field=syntax['symbols'][i][0]
                        value=match.groups()[i]
                        #
                        #fields need some validation,
                        #register must exist OR value must be numeric
                        #
                        if value not in self._registers and type(value) != int:
                            try:
                                if value[:2] == '0x':
                                    value=int(value,base_16)
                                else:
                                    value=int(value)
                            except:
                                raise Bad_instruction_or_syntax(line)
                        self.log.buffer("`{0}' is {1}".format(field,value))
                        instruction_fields[field]=value

                    #
                    #we want to build a complete instruction
                    #
                    values=self._instruction_values[instruction]
                    for field in values:
                        instruction_fields[field]=values[field]
                    format_name = self._format_mappings[instruction]

                    instruction_raw=self._isa_size*'0'.split()
                    for field in instruction_fields:
                        start=self._format_properties[format_name][field][0]
                        end=self._format_properties[format_name][field][1]+1
                        if instruction_fields[field] in self._registers:
                            value = self._registers[instruction_fields[field]]
                        else:
                            value = instruction_fields[field]
                        width = end - start
                        instruction_raw[start:end]=bin(value, size=width)[2:]
                    instruction_raw = "".join(instruction_raw)
                    output.append(instruction_raw)
                    self.log.buffer("encoded {0}".format(instruction_raw))
                else:
                    raise Bad_instruction_or_syntax(line)
            #elif instruction in self._special_instructions:
                #
                #we aren't dealing with specials yet
                #this will probably come into play with assembler directives
                #
                #output.append(instruction)
                #pass
            else:
                raise Bad_instruction_or_syntax(line)
            instruction_fields.clear()
        self.log.buffer("leaving encoder")
        return output




if __name__ == '__main__':
    import unittest
    import Isa
    import System

    from lib.Logger import Logger, InterpreterLogger
    from lib.XmlLoader import InstructionReader, MachineReader

    class TestInterpreter(unittest.TestCase):

        def setUp(self):
            ir=InstructionReader('../../xml/instructions.xml')
            mr=MachineReader('../../xml/machine.xml')

            address_space=mr.getAddressSpace()
            instructions=Isa.InstructionSet('MIPS_I', 32)
            memory=System.Memory(address_space, instructions)

            registers=System.Registers()
            #
            #add assembly syntax to the instruction set
            #
            asmsyntax=ir.getAssemblySyntax()
            for element in asmsyntax:
                instructions.addAssemblySyntax(element, asmsyntax[element])

            register_mappings=mr.getRegisterMappings()
            memory.addSegment('text', int('0x400000',16), int('0x7fffffff',16))
            for mapping in register_mappings:
                registers.addRegisterMapping(mapping, register_mappings[mapping])
            #
            #interpreter is created here
            #
            self.interpreter=Interpreter(instructions, registers, memory)

            logger=Logger('unittest.log')
            self.interpreter.openLog(logger)
            memory.openLog(logger)
            #
            #add instruction syntax to the instruction set
            #
            syntax=ir.getSyntax()
            for instruction in syntax:
                instructions.addSyntax(instruction, syntax[instruction])
            formats=ir.getFormatMapping()
            for format in formats:
                instructions.addFormatMapping(format, formats[format])
            values=ir.getValues()
            for instruction in values:
                instructions.addValue(instruction, values[instruction] )
            properties=ir.getFormatProperties()
            for prop in properties:
                instructions.addFormatProperty(prop, properties[prop])
            self.programme1=['#Tom Regan <thomas.c.regan@gmail.com>\n',
                             '#2011-07-04\n', '#add.asm-- Computes the sum of 1 and 2\n',
                             '#modifies: t0 (result)\n',
                             '#          t1 (operand)\n',
                             'Main:    addi  $t0, $zero, 2  #t0 <- 2\n',
                             '         addi  $t1, $zero, 2  #t1 <- 2\n',
                             '         add   $t0, $t0,  $t1 #t0 <- 2 + 2\n',
                             'Exit:',
                             '         addi $v0, $zero, 10']
            self.programme2=['Main:    addi  $t0, $zero, 10\n',
                             'Loop:    beq   $t0, $t1,   Exit\n',
                             '         addi  $t0, $zero, -1\n',
                             '         j     Loop\n',
                             'Exit:']


        def tearDown(self):
            pass

        def testPreprocessor(self):
            #
            #we expect a table of labels and their offsets
            #
            good_jump_table1={'Main': 0, 'Exit': 3}
            #
            #we don't expect to see comments or other
            #text-file formatting
            #
            good_programme1=['addi  $t0, $zero, 2',
                             'addi  $t1, $zero, 2',
                             'add   $t0, $t0,  $t1',
                             'addi $v0, $zero, 10']
            good_programme2=['addi  $t0, $zero, 10',
                             'beq   $t0, $t1,   Exit',
                             'addi  $t0, $zero, -1',
                             'j     Loop']
            result1=self.interpreter._preprocess(self.programme1)

            self.assertEquals(good_programme1, result1)
            self.assertEquals(good_jump_table1, self.interpreter._jump_table)

            good_jump_table2={'Main': 0, 'Exit': 4, 'Loop':1}
            result2=self.interpreter._preprocess(self.programme2)
            self.assertEquals(good_jump_table2, self.interpreter._jump_table)
            self.assertEquals(good_programme2, result2)

        def testLinker(self):
            good_programme2=['addi $t0, $zero, 10',
                             'beq $t0, $t1, 0x4',
                             'addi $t0, $zero, -1',
                             'j 0x1']
            programme2=self.interpreter._preprocess(self.programme2)
            programme2=self.interpreter._link(programme2)

            self.assertEquals(good_programme2, programme2)

        def testEncoder(self):
            #
            #This instruction and its encoding is taken from PH.
            #
            instruction=['add $t0,$s1,$s2']
            good_result1=['00000010001100100100000000100000']
            result1=self.interpreter._preprocess(instruction)
            self.assertEquals(result1, instruction)
            result1=self.interpreter._link(result1)
            self.assertEquals(result1, instruction)
            result1=self.interpreter._encode(result1)
            self.assertEquals(good_result1, result1)
            #
            #The following is verified against SPIM,
            #which was kind enough to have a dump.
            #
            good_result2=['00100000000010000000000000000010',
                          '00100000000010010000000000000010',
                          '00000001000010010100000000100000',
                          '00100000000000100000000000001010']
            syscall=     ['00000000000000000000000000001100']
            result2=self.interpreter._preprocess(self.programme1)
            result2=self.interpreter._link(result2)
            result2=self.interpreter._encode(result2)
            self.assertEquals(good_result2, result2)

        def testReadLine(self):
            good_result1=['00000010001100100100000000100000']
            result1=self.interpreter.read_lines('add $t0,$s1,$s2')
            self.assertEquals(good_result1, result1)

        def testReadFile(self):
            good_result1=['00100000000010000000000000000010',
                          '00100000000010010000000000000010',
                          '00000001000010010100000000100000',
                          '00100000000000100000000000001010']
            good_result2=['00100000000010000000000000001010',
                          '00010001000010010000000000000100',
                          '00100000000010001111111111111111',
                          '00001000000000000000000000000001']
            file_object1=open('../../asm/add.asm','r')
            result1=self.interpreter.readFile(file_object1)
            self.assertEquals(good_result1, result1)

            file_object2=open('../../asm/labels.asm','r')
            result2=self.interpreter.readFile(file_object2)
            self.assertEquals(good_result2, result2)



    tests = unittest.TestLoader().loadTestsFromTestCase(TestInterpreter)
    unittest.TextTestRunner(verbosity=2).run(tests)
