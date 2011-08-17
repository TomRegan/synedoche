#!/usr/bin/env python
''' XmlLoader.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-06-23
modified:    2011-07-19
description: Module providing support for XML functions
'''

from xml.dom.minidom import parse
from Functions       import asciify

class XmlDocument(object):
    """Provides a basic interface to an XML file"""
    def __init__(self, filename):
        self.__xmlDoc=parse(filename)
        self._rootNode=self.__xmlDoc.documentElement

    def openDocument(self, filename):
        self.__xmlDoc=parse(filename)
        self._rootNode=self.__xmlDoc.documentElement




class XmlDataFormatException(Exception):
    """Xml file is not valid """
    pass


class XmlReader(object):
    """Provides storage for derrived classes """

    _data={}




class InstructionReader(XmlReader):
    """A class to parse an instruction.xsd-validated isa specification

    Typical usage looks like this:
        reader=InstructionReader() --creates a new reader
        isa=reader.getRecord()     --returns a record class
        isa.language               --outputs `language'

    Record fields are:
        language       --string language name
        size           --string instruction size
        formats        --dict   instruction set:string->(field:string)
        signatures     --dict   instruction signatures:string->(field:string)
        syntax         --dict   instruction name:string->(symbol:string)
        fields         --dict   instruction name:string->(field:string)
        implementation --dict   instruction name:string->(call:string)

        Implementation:
            api calls are documented ... elsewhere
    """

    def __init__(self, filename):
        self._document=XmlDocument(filename)
        self._rootNode=self._document._rootNode
        self._readLanguage()
        self._readSize()
        self._readFormatFieldSizeMap()
        self._readInstructionSignatureMap()
        self._readInstructionSyntaxMap()
        self._readInstructionValuesMap()
        self._readInstructionImplementationMap()
        self._readInstructionFormatMap()
        self._readAssembleyDirectives()
        self._read_replacements()
        #below will be a part of the new api
        self._read_assembler_syntax()
        self._read_instructions()

    def _readLanguage(self):
        """Stores 'language' -> self.record

        Reads an xml machine instruction specification and looks for the
        language of the instruction set.
        """
        self.language=self._rootNode.attributes['language'].value.encode('ascii')

    def _readSize(self):
        """Stores 'size' -> self.record

        Reads an xml machine instruction specification and looks for the
        size in bits of the instruction set.
        """
        size=self._rootNode.attributes['size'].value.encode('ascii')
        self.size=int(size,16)


    def _readFormatFieldSizeMap(self):
        """Stores {format name : {field : [start, end]}} -> self.record

        Reads an xml machine instruction specification and looks for
        instruction format data.
        """
        formats={}
        formatRoot=self._rootNode.getElementsByTagName('formats')[0]
        formatNodeList=formatRoot.getElementsByTagName('format')

        for node in formatNodeList:
            typ=node.attributes['type'].value.encode('ascii')
            formats[typ]={}
            formatFields=node.getElementsByTagName('field')
            for field in formatFields:
                name  = field.attributes['name'].value.encode('ascii')
                start = field.attributes['start'].value.encode('ascii')
                end   = field.attributes['end'].value.encode('ascii')
                #Cpu wants a hash:{hash:(tuple)} struct for its lookups
                formats[typ][name]=(int(start,16), int(end,16))
        self.formatFieldSize=formats

    def _readInstructionSignatureMap(self):
        """Stores {instruction name : [fields]} -> self.record

        Reads an xml machine instruction specification and looks for
        the signatures (unique opcode elements) used to decode
        instructions.

        This is necessary because certain instruction formats re-use
        the same opcode for numerous instructions, and rely on another
        bit-field to decode the instruction.
        """
        signatures={}
        instructionNodeList=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            instructionName=instruction.attributes['name'].value.encode('ascii')
            signatures[instructionName]=[]
            signatureNode=instruction.getElementsByTagName('signature')
            fieldNodeList=signatureNode[0].getElementsByTagName('field')
            for field in fieldNodeList:
                fieldName=field.attributes['name'].value.encode('ascii')
                signatures[instructionName].append(fieldName)
        self.instructionSignature=signatures

    def _readInstructionSyntaxMap(self):
        """Stores {instruction name : syntax} -> self.record

        Reads an xml instruction specification and looks for the assembly
        syntax used to describe instructions.
        """
        syntax={}
        instructionNodeList=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            instructionName=instruction.attributes['name'].value.encode('ascii')
            syntax[instructionName]={'expression':[],'symbols':[]}
            syntaxNode=instruction.getElementsByTagName('syntax')
            expression=syntaxNode[0].getElementsByTagName('expression')[0].attributes['pattern'].value.encode('ascii')
            symbolNodeList=syntaxNode[0].getElementsByTagName('symbol')
            syntax[instructionName]['expression']=expression
            for symbol in symbolNodeList:
                kind=symbol.attributes['type'].value.encode('ascii')
                match=symbol.attributes['matches'].value.encode('ascii')
                syntax[instructionName]['symbols'].append((match,kind))
        self.instructionSyntax=syntax

    def _readInstructionValuesMap(self):
        """Stores {instruction name : {field : value}} -> self.record

        Reads an xml instruction specification and looks for the pre-set
        fields for each instruction.
        """
        fields={}
        instructionNodeList=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            instructionName=instruction.attributes['name'].value.encode('ascii')
            fields[instructionName]={}
            fieldsNode=instruction.getElementsByTagName('fields')
            fieldNodeList=fieldsNode[0].getElementsByTagName('field')
            for field in fieldNodeList:
                name=field.attributes['name'].value.encode('ascii')
                value=field.attributes['value'].value.encode('ascii')
                fields[instructionName][name]=int(value,16)
        self.instructionValues=fields

    def _readInstructionImplementationMap(self):
        """Stores {instruction name : (method, [args])} -> self.record

        Reads an xml instruction specification and looks for the
        api calls used to implement each instruction.
        """
        methods={}
        instructionNodeList=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            instructionName=instruction.attributes['name'].value.encode('ascii')
            methods[instructionName]=[]
            implementationNode=instruction.getElementsByTagName('implementation')
            methodNodeList=implementationNode[0].getElementsByTagName('method')
            for method in methodNodeList:
                name=method.attributes['name'].value.encode('ascii')
                args=method.attributes['args'].value.encode('ascii').split()
                for i in range(len(args)):
                    if args[i][:2] == '0x':
                        args[i] = int(args[i],16)
                methods[instructionName].append((name,args))
        self.instructionImplementation=methods

    def _readInstructionFormatMap(self):
        """Stores a dict of instruction : format

        Reads an XML instruction specification and looks for the
        format of each instruction
        """
        instructionFormats={}
        instructionNodeList=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            instructionName   = instruction.attributes['name'].value.encode('ascii')
            instructionFormat = instruction.attributes['format'].value.encode('ascii')
            instructionFormats[instructionName]=instructionFormat
        self.instructionFormats=instructionFormats

    def _read_replacements(self):
        instructions=self._rootNode.getElementsByTagName('instruction')
        i_replacements=[]
        for instruction in instructions:
            i_name  = asciify(instruction.attributes['name'].value)
            try:
                r_root = instruction.getElementsByTagName('replacements')[0]
                replacements = r_root.getElementsByTagName('replacement')
                for replacement in replacements:
                    r_name  = asciify(replacement.attributes['name'].value)
                    r_group = asciify(replacement.attributes['group'].value)
                    r_type  = asciify(replacement.attributes['type'].value)
                    i_replacements.append((i_name, r_name, r_group, r_type))
            except Exception, e:
                #if i_name == 'j': raise e
                #else: pass
                pass
        self._data['replacements'] = tuple(i_replacements)

    def _read_instructions(self):
        data=[]
        instructions=self._rootNode.getElementsByTagName('instruction')
        for instruction in instructions:
            # add attributes
            i_name   = asciify(instruction.attributes['name'].value)
            i_format = asciify(instruction.attributes['format'].value)

            # add signatures
            i_signature=[]
            s_root = instruction.getElementsByTagName('signature')[0]
            fields = s_root.getElementsByTagName('field')
            for field in fields:
                f_name = asciify(field.attributes['name'].value)
                i_signature.append(f_name)
            i_signature = tuple(i_signature)

            # add preset values
            i_values=[]
            f_root = instruction.getElementsByTagName('fields')[0]
            fields = f_root.getElementsByTagName('field')
            for field in fields:
                f_name  = asciify(field.attributes['name'].value)
                f_value = asciify(field.attributes['value'].value)
                i_values.append((f_name, int(f_value, 16)))
            i_values = tuple(i_values)

            # add syntax
            i_syntax=[]
            s_root = instruction.getElementsByTagName('syntax')[0]
            fields = s_root.getElementsByTagName('field')
            expression   = s_root.getElementsByTagName('expression')[0]
            symbols = s_root.getElementsByTagName('symbol')
            for symbol in symbols:
                s_kind=symbol.attributes['type'].value
                s_match=symbol.attributes['matches'].value
                i_syntax.append((asciify(s_match), asciify(s_kind)))
            i_expression = asciify(expression.attributes['pattern'].value)
            i_syntax = tuple(i_syntax)

            # add implementation
            i_implementation=[]
            im_root = instruction.getElementsByTagName('implementation')[0]
            methods = im_root.getElementsByTagName('method')
            for method in methods:
                im_name = method.attributes['name'].value
                im_args = method.attributes['args'].value
                i_implementation.append(asciify(im_name))
                i_implementation.append(asciify(im_args))
            i_implementation = tuple(i_implementation)

            # add replacements
            i_replacements=[]
            try:
                r_root = instruction.getElementsByTagName('replacements')[0]
                replacements = r_root.getElementsByTagName('replacement')
                for replacement in replacements:
                    r_name  = asciify(replacement.attributes['name'].value)
                    r_group = asciify(replacement.attributes['group'].value)
                    r_type  = asciify(replacement.attributes['type'].value)
                    i_replacements.append((r_name, r_group, r_type))
            except Exception, e:
                pass
            i_replacements = tuple(i_replacements)

            instruction=(i_name, i_format, i_signature,
                         i_expression, i_values, i_syntax,
                         i_implementation, i_replacements)

            data.append(instruction)
        self._data['instructions'] = tuple(data)

    def _readAssembleyDirectives(self):
        """{ name:<string> : profile:<string> } -> assembler_directives

        Reads an XML instruction specification and looks for the
        assembler directives.
        """

        self._assembley_directives={}
        directivesNodesList=self._rootNode.getElementsByTagName('assembler')[0]\
            .getElementsByTagName('directives')[0].getElementsByTagName('directive')
        for directive in directivesNodesList:
            name    = directive.attributes['name'].value.encode('ascii')
            profile = directive.attributes['profile'].value.encode('ascii')
            self._assembley_directives[name] = profile

    def _read_assembler_syntax(self):
        """{ name:<string> : pattern:<string> } -> assembler_syntax

        Reads an XML instruction specification and looks for the
        assembler syntax.
        """

        assembler = self._rootNode.getElementsByTagName('assembler')[0]
        assembler_syntax = assembler.getElementsByTagName('syntax')[0]
        label     = assembler_syntax.getElementsByTagName('label')[0]
        reference = assembler_syntax.getElementsByTagName('reference')[0]
        comment   = assembler_syntax.getElementsByTagName('comment')[0]

        data=[]
        for element in [label, reference, comment]:
            name = element.tagName.encode('ascii')
            pattern = element.attributes['pattern'].value.encode('ascii')
            data.append((name, pattern))
        self._data['assembler']=tuple(data)

    def getLanguage(self):
        """-> language:<string>"""
        return self.language

    def getSize(self):
        """-> size:<int>"""
        return self.size

    def getSyntax(self):
        """-> {instruction name:<string> : syntax:<list>}"""
        return self.instructionSyntax

    def getImplementation(self):
        """-> """
        return self.instructionImplementation

    def getValues(self):
        """-> """
        return self.instructionValues

    def getSignatures(self):
        """-> """
        return self.instructionSignature

    def getFormatMapping(self):
        """-> """
        return self.instructionFormats

    def getFormatProperties(self):
        """-> """
        return self.formatFieldSize

    def getAssemblyDirectives(self):
        """-> {name:<string> : profile:<string>}"""
        return self._assembley_directives

    def get_replacements(self):
        """get_replacements() ->
        """
        return self._data['replacements']

    def get_assembler_syntax(self):
        """get_assembler_syntax() ->
           ((label:str,     pattern:str),
            (reference:str, pattern:str),
            (comment:str,   pattern:str)):tuple
        """
        return self._data['assembler']

    def get_instructions(self):
        return self._data['instructions']




class MachineReader(XmlReader):
    """A class to parse a machine.xsd-validated machine specification

    Usage:
        All the functions return a data structure.

        getLanguage()         ->   language:str
        getMemory()           ->   {segment:str->[start:int,end:int]:list}:dict
        getAddressSpace()     ->   [start:int,end:int]:list
        getRegisters()        ->   {number:int->{value:int}:dict
                                                {value:int}:dict
                                                {privilege:bool}:dict
                                                {profile:str}:dict
                                   }:dict
        getRegisterMappings() -> {name:str->number:int}:dict

    Privilege determines whether a register is user-writable.

    Profile may be one of:
        gp (general purpose), PC (programme counter), psw (status)

    In the case of register mappings, each number value is a reference
    to an index of registers.
    """

    _language=None
    _address_space=None
    _memory={}
    _registers={}
    _register_mappings={}

    def __init__(self, filename):
        self._document=XmlDocument(filename)
        self._rootNode=self._document._rootNode
        self._readLanguage()
        self._read_memory()
        self._readRegisters()
        self._read_pipeline()

    def _readLanguage(self):
        """Stores the language recognized by the machine implementation

        Reads an xml machine specification and looks for the language
        recognised by that machine.
        """
        self._language=self._document._rootNode.getElementsByTagName('language')[0].attributes['name'].value.encode('ascii')

    def _read_memory(self):
        """Stores a segmentation profile for the machine's memory

        Reads an xml machine specification and looks for details
        of its memory organization.
        """
        memory=[]

        memory_node=self._rootNode.getElementsByTagName('memory')[0]
        address_space = asciify(memory_node.attributes['address_space'].value)
        word          = asciify(memory_node.attributes['word'].value)
        addressable   = asciify(memory_node.attributes['addressable'].value)

        for attribute in [address_space, word, addressable]:
            #readable, but a potential bug for non-hex data
            memory.append(int(attribute, 16))

        text_node  = memory_node.getElementsByTagName('text')[0]
        data_node  = memory_node.getElementsByTagName('data')[0]
        stack_node = memory_node.getElementsByTagName('stack')[0]
        for segment in [text_node, data_node, stack_node]:
            s_name  = asciify(segment.tagName)
            s_start = int(asciify(segment.attributes['start'].value), 16)
            s_end   = int(asciify(segment.attributes['end'].value), 16)
            memory.append((s_name, s_start, s_end))
        self._address_space=[0,int(address_space,16)]
        self._data['memory']=tuple(memory)

    def _readRegisters(self):
        """Stores a register profile and associated data

        Reads an xml machine specification and looks for details
        of the registers.

        Generates a number:name lookup table for the use of
        the interpreter
        """
        registers_node=self._rootNode.getElementsByTagName('registers')
        register_node_list=registers_node[0].getElementsByTagName('register')
        for register in register_node_list:
            name    = register.attributes['name'].value.encode('ascii')
            number  = register.attributes['number'].value.encode('ascii')
            size    = register.attributes['size'].value.encode('ascii')
            write   = register.attributes['write'].value.encode('ascii')
            profile = register.attributes['profile'].value.encode('ascii')
            visible = asciify(register.attributes['visible'].value)
            number = int(number,16)
            self._registers[number]={}
            self._registers[number]['size']      = int(size,16)
            self._registers[number]['privilege'] = bool(write)
            self._registers[number]['profile']   = profile
            self._registers[number]['visible']   = bool(visible)
            self._register_mappings[name]=number
            #
            #all the registers are initialized to zero
            #
            self._registers[number]['value']=0
        #
        #each register _may_ have a preset value, eg. instruction pointer
        #
        presets_node=self._rootNode.getElementsByTagName('presets')
        preset_node_list=presets_node[0].getElementsByTagName('preset')
        for preset in preset_node_list:
            number = asciify(preset.attributes['number'].value)
            value  = asciify(preset.attributes['value'].value)
            number = int(number, 16)
            if number in self._registers:
                self._registers[number]['value']=int(value, 16)
            else:
                raise XmlDataFormatException()

    def _read_pipeline(self):
        pipeline = self._rootNode.getElementsByTagName('pipeline')[0]
        stages   = pipeline.getElementsByTagName('stage')

        self._pipeline_stages = []
        for stage in stages:
            name = asciify(stage.attributes['name'].value)
            self._pipeline_stages.append(name)


    def getLanguage(self):
        """-> language:string"""
        return self._language

    def get_memory(self):
        """get_memory() ->
            (size:int, word:int, addressable:int,
             (segment:str, start:int, end:int):tuple):tuple
        """
        return self._data['memory']

    def getAddressSpace(self):
        """-> address_space:int"""
        return self._address_space

    def getRegisters(self):
        """-> """
        return self._registers

    def getRegisterMappings(self):
        """-> """
        return self._register_mappings

    def get_pipeline(self):
        """get_pipeline() -> (stage:str):tuple"""
        return tuple(self._pipeline_stages)




if __name__ == '__main__':
    reader=InstructionReader('../config/instructions.xml')
    #print reader.get_replacements()
    #print reader.get_instructions()[8][2][0]
    #print reader.getAssembleyDirectives()
    #print reader.getAssembleySyntax()
    #language=reader.getLanguage()
    #size=reader.getSize()
    #print "Success: read `{0}', a {1:2d}-bit ISA\n".format(language,int(size,16))
    #print "Language: {0}\n".format(isa.language)
    #print "Size: {0}\n".format(isa.size)
    #print "Formats: {0}\n".format(reader.getFormatProperties())
    #print "Field values: {0}\n".format(reader.getValues())
    #print "Signatures: {0}\n".format(reader.getSignatures())
    #print "Syntax: {0}\n".format(reader.getSyntax())
    #print "Implementation: {0}\n".format(reader.getImplementation())
    #print "InstructionFormats: {0}".format(reader.getFormatMapping())

    reader=MachineReader('../config/machine.xml')
    #print reader.get_pipeline()
    #print "Success: read `{0}' from file".format(machine.language)
    #print machine.registerPrivilege
    #print reader.getLanguage()
    #print reader.getAddressSpace()
    #print reader.get_memory()
    #print reader.getRegisters()
    #print reader.getRegisterMappings()
