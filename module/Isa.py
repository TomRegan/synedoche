#!/usr/bin/env python
''' Isa.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-05
modified:    2011-07-09
description: Instruction set architecture features
'''

from lib.Functions import dumpAccessors

class InstructionSet(object):
    """Provides an interface that should be used to load an ISA
    """

    _language=None
    _size=None
    _instruction_implementation={}
    _instruction_fields={}
    _instruction_signature={}
    _instruction_format={}
    _instruction_syntax={}
    _format_fields={}
    _assembly_syntax={}
    _assembly_directives={}
    def __init__(self, language, size):
        """(language:str, size:int) -> ...

        Usage:
            instructions=InstructionSet('intel_IA64')
            instructions.addImplementation('add', [('addRegisters', ['rd','rs','rt'])])
            ...
            instructions.addValues('add': {'sa': 0, 'fn': 32, 'op': 0})
            instructions.addSignature('add', {'op', [0, 5]}, {'fn', [26, 31]})
            instructions.addFormat('r', {'op':[0,5],'fn':[26,31],'rs':[6,10],'rt':[11,15],'rd':[16,20],'sa':[21,25]})
            instructions.addFormatMapping('add', 'r')
        """
        self._language = language
        self._size     = size

    def addImplementation(self, instruction, methods):
        """(instruction:str, [(methods:str,[field:str]:list):tuple]:list) ->
            {instruction:[methods:str,[field:str]:list}:dict

        Stores implementation data.

        Raises:
            Exception
        """

        if len(methods) < 1:
            raise Exception
        self._instruction_implementation[instruction]=methods

    def addValue(self, instruction, fields):
        """(instruction:str, {fields:str:value:int}:dict) ->
            implementation{instruction:{field:value}:dict}:dict

        Stores preset values for instruction fields.

        Raises:
            Exception
        """

        if len(fields) < 1:
            raise Exception
        self._instruction_fields[instruction]=fields

    def addSignature(self, instruction, fields):
        """(instruction:str, {fields:str:value:int}:dict) ->
            implementation{instruction:{field:value}:dict}:dict

        Stores instruction signatures.

        Raises:
            Exception
        """

        if len(fields) < 1:
            raise Exception
        self._instruction_signature[instruction] = fields

    def addFormatProperty(self, format_name, fields):
        """(format:str, {fields:str:[start:int,end:int]:list}:dict) ->
            formats{format:{field:str:[start:int,end:int]:list}:dict}:dict

        Stores bit ranges for format fields.

        Raises:
            Exception
        """

        if len(fields) < 1:
            raise Exception
        self._format_fields[format_name] = fields

    def addSyntax(self, instruction, syntax):
        """(instruction:str, syntax{symbols:str:[field:str]
                                    expression:str}:dict) ->
                 (instruction:str, syntax{symbols:str:[field:str]
                                          expression:str}:dict)

        Stores regular expressions(['expression']) and mappings in
        order of regex group-match.
        """

        if len(syntax) < 1:
            raise Exception
        self._instruction_syntax[instruction] = syntax

    def addFormatMapping(self, instruction, format_name):
        """(instruction:str, format_name:str) ->
                instructions{instruction:format}:dict

        Stores instruction to format mappings.
        """
        self._instruction_format[instruction] = format_name

    def addAssemblySyntax(self, name, pattern):
        """(name:str, pattern:str) -> {name:pattern}:dict

        Stores elements of assembly syntax, including labels
        and comment patterns.
        """
        self._assembly_syntax[name] = pattern

    def addAssemblyDirective(self, name, profile):
        self._assembly_directives[name] = profile

    def getLanguage(self):
        return self._language

    def getSize(self):
        return self._size

    def getImplementation(self):
        return self._instruction_implementation

    def getValues(self):
        return self._instruction_fields

    def getSignatures(self):
        return self._instruction_signature

    def getSyntax(self):
        return self._instruction_syntax

    def getFormatMapping(self):
        return self._instruction_format

    def getFormatProperties(self):
        return self._format_fields

    def getAssemblySyntax(self):
        return self._assembly_syntax

    def getAssemblyDirectives(self):
        return self._assembly_directives
