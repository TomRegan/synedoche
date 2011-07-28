#!/usr/bin/env python
#
# Instructions.
# file           : Isa.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-05
# last modified  : 2011-07-24


from lib.Functions import dump_accessors

class BaseIsa(object):
    _data={}

class Isa(BaseIsa):
    def set_global_language(self, language):
        self._data['global_language'] = language

    def set_global_size(self, size):
        self._data['global_size'] = size

    def add_mapping(self, instruction, format_name):
        if not self._data.has_key('itof'):
               self._data['itof'] = {}
        self._data['itof'][instruction]=format_name
        if not self._data.has_key('ftoi'):
               self._data['ftoi'] = {}
        self._data['ftoi'][format_name]=instruction

    def add_instruction_implementation(self, instruction, methods, *args):
        if not self._data.has_key('instruction_implementation'):
               self._data['instruction_implementation'] = {}
        self._data['instruction_implementation'][instruction]=methods

    def add_instruction_preset(self, instruction, presets, *args):
        if not self._data.has_key('instruction_presets'):
               self._data['instruction_presets'] = {}
        local_data={}
        for (field,value) in presets:
            local_data[field] = value
        self._data['instruction_presets'][instruction]=local_data

    def add_instruction_signature(self, instruction, signatures, presets, *args):
        #implementation{instruction:{field:value}:dict}:dict
        if not self._data.has_key('instruction_signatures'):
               self._data['instruction_signatures'] = {}
        local_data={}
        for signature in signatures:
            for preset in presets:
                if signature == preset[0]:
                    local_data[signature] = preset[1]
        self._data['instruction_signatures'][instruction]=local_data

    def add_instruction_syntax(self, instruction, pattern, symbols, *args):
        if not self._data.has_key('instruction_syntax'):
               self._data['instruction_syntax'] = {}
        self._data['instruction_syntax'][instruction]={'expression':pattern,
                                                       'symbols'   :symbols}

    def add_instruction_replacement(self, instruction, replacement, *args):
        if len(replacement) > 0:
            if not self._data.has_key('instruction_replacement'):
                   self._data['instruction_replacement'] = {}
            self._data['instruction_replacement'][instruction]=replacement

    def add_assembler_syntax(self, patterns, *args):
        local_data={}
        for (name, pattern) in patterns:
            local_data[name] = pattern
        self._data['assembler_syntax'] = local_data

    def add_format_properties(self, format_name, fields, *args):
        if not self._data.has_key('format_properties'):
               self._data['format_properties'] = {}
        local_data={}
        for (field, start, end) in fields:
            local_data[field] = (start, end)
        self._data['format_properties'][format_name]=local_data

    def getLanguage(self):
        return self._data['global_language']

    def getSize(self):
        return self._data['global_size']

    def getImplementation(self):
        return self._data['instruction_implementation']

    def getValues(self):
        return self._data['instruction_presets']

    def getSignatures(self):
        return self._data['instruction_signatures']

    def getSyntax(self):
        return self._data['instruction_syntax']

    def getFormatMapping(self):
        return self._data['itof']

    def get_mapping_to_instruction(self):
        return self._data['ftoi']

    def getFormatProperties(self):
        return self._data['format_properties']

    def getAssemblySyntax(self):
        return self._data['assembler_syntax']

    def get_assembly_syntax(self):
        return self._data['assembler_syntax']

    def get_label_replacements(self):
        return self._data['instruction_replacement']

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
    _label_replacement={}
    _format_fields={}
    _assembly_syntax={}
    _assembly_directives={}
    def __init__(self, language, size):
        """(language:str, size:int) -> ...

        Usage:
            instructions=InstructionSet('intel_IA64')
            instructions.addImplementation('add', [('add_registers', ['rd','rs','rt'])])
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

    def add_label_replacement(self, instruction, replacement):
        """instruction:str, replacement:tuple"""
        self._label_replacement[instruction] = replacement

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

    def add_assembler_syntax(self, name, pattern):
        """{name:str, pattern:str}:dict

        Stores elements of assembly syntax, including labels
        and comment patterns.
        """
        self._assembly_syntax[name] = pattern

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

    #def getAssemblyDirectives(self):
    #    return self._assembly_directives

    def get_assembly_syntax(self):
        return self._assembly_syntax

    def get_label_replacements(self):
        return self._label_replacement
