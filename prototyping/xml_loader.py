#!/usr/bin/env python

''' xml_loader.py
author:      Tom Regan <code.tregan@gmail.com>
since:       2011-06-23
modified:    2011-06-26
description: prototype xml parser
'''

from xml.dom.minidom import parse

class XmlDocument(object):
    """Provides a basic interface to an XML file"""
    def __init__(self, filename):
        self.__xmlDoc=parse(filename)
        self.rootNode=self.__xmlDoc.documentElement

    def openDocument(self, filename):
        self.__xmlDoc=parse(filename)
        self.rootNode=self.__xmlDoc.documentElement




class XmlDataFormatException(Exception):
    """Xml file is not valid """
    pass


class XmlReader(object):
    """Provides storage for derrived classes """

    class Record(object):
        """A machine record """
        pass

    def getRecord(self):
        """Returns a record containing data extracted from an XML file"""
        return self.Record




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
        self.document=XmlDocument(filename)
        self.rootNode=self.document.rootNode
        self.getLanguage()
        self.getSize()
        self.getFormats()
        self.getSignatures()
        self.getSyntax()
        self.getFields()
        self.getImplementation()

    def getLanguage(self):
        """Stores the language of the instruction set

        Reads an xml machine instruction specification and looks for the
        language of the instruction set.
        """
        self.Record.language=self.rootNode.attributes['language'].value.encode('ascii')

    def getSize(self):
        """Stores the size of the instruction set

        Reads an xml machine instruction specification and looks for the
        size in bits of the instruction set.
        """
        self.Record.size=self.rootNode.attributes['size'].value.encode('ascii')


    def getFormats(self):
        """Stores a dict of name : field/bit-offsets for instructions

        Reads an xml machine instruction specification and looks for
        instruction format data.
        """
        formats={}
        formatRoot=self.rootNode.getElementsByTagName('formats')[0]
        formatNodeList=formatRoot.getElementsByTagName('format')

        for node in formatNodeList:
            #walk the list of formats
            typ=node.attributes['type'].value.encode('ascii')
            formats[typ]={}
            formatFields=node.getElementsByTagName('field')
            for field in formatFields:
                #walk the list of field attributes
                name  = field.attributes['name'].value.encode('ascii')
                start = field.attributes['start'].value.encode('ascii')
                end   = field.attributes['end'].value.encode('ascii')
                #Cpu wants a hash:{hash:(tuple)} struct for its lookups
                formats[typ][name]=(start, end)
        self.Record.formats=formats

    def getSignatures(self):
        """Stores a dict of name : field(s)

        Reads an xml machine instruction specification and looks for
        the signatures (unique opcode elements) used to decode
        instructions.

        This is necessary because certain instruction formats re-use
        the same opcode for numerous instructions, and rely on another
        bit-field to decode the instruction.
        """
        signatures={}
        instructionNodeList=self.rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            #walk the list of instructions"""
            instructionName=instruction.attributes['name'].value.encode('ascii')
            signatures[instructionName]=[]
            signatureNode=instruction.getElementsByTagName('signature')
            fieldNodeList=signatureNode[0].getElementsByTagName('field')
            for field in fieldNodeList:
                #walk the list of fields in the signature node
                fieldName=field.attributes['name'].value.encode('ascii')
                signatures[instructionName].append(fieldName)
        self.Record.signatures=signatures

    def getSyntax(self):
        """Stores a dict of name : syntax

        Reads an xml instruction specification and looks for the assembly
        syntax used to describe instructions.
        """
        syntax={}
        instructionNodeList=self.rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            #walk the list of instructions
            instructionName=instruction.attributes['name'].value.encode('ascii')
            syntax[instructionName]=[]
            syntaxNode=instruction.getElementsByTagName('syntax')
            symbolNodeList=syntaxNode[0].getElementsByTagName('symbol')
            for symbol in symbolNodeList:
                #walk the list of symbols under syntax
                kind=symbol.attributes['type'].value.encode('ascii')
                match=symbol.attributes['matches'].value.encode('ascii')
                syntax[instructionName].append((match,kind))
        self.Record.syntax=syntax

    def getFields(self):
        """Stores a dict of name : fields

        Reads an xml instruction specification and looks for the pre-set
        fields for each instruction.
        """
        fields={}
        instructionNodeList=self.rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            #walk the list of instructions
            instructionName=instruction.attributes['name'].value.encode('ascii')
            fields[instructionName]={}
            fieldsNode=instruction.getElementsByTagName('fields')
            fieldNodeList=fieldsNode[0].getElementsByTagName('field')
            for field in fieldNodeList:
                #walk the list of symbols under syntax
                name=field.attributes['name'].value.encode('ascii')
                value=field.attributes['value'].value.encode('ascii')
                fields[instructionName][name]=value
        self.Record.fields=fields

    def getImplementation(self):
        """Stores a dict of name : method/[args]

        Reads an xml instruction specification and looks for the
        api calls used to implement each instruction.
        """
        methods={}
        instructionNodeList=self.rootNode.getElementsByTagName('instruction')
        for instruction in instructionNodeList:
            #walk the list of instructions
            instructionName=instruction.attributes['name'].value.encode('ascii')
            methods[instructionName]=[]
            implementationNode=instruction.getElementsByTagName('implementation')
            methodNodeList=implementationNode[0].getElementsByTagName('method')
            for method in methodNodeList:
                #walk the list of methods
                name=method.attributes['name'].value.encode('ascii')
                args=method.attributes['args'].value.encode('ascii')
                methods[instructionName].append((name,args.split()))
        self.Record.implementation=methods




class MachineReader(XmlReader):
    """A class to parse a machine.xsd-validated machine specification

    Typical usage looks like this:
        reader=MachineReader()     --creates a new reader
        machine=reader.getRecord() --returns a record class
        machine.language           --outputs `language'

    Record fields are:
        language          --string language name(string)
        memory            --dict   (data,stack,text)->(start,end)
        registerValue     --dict   register number:string->value:string
        registerSize      --dict   register number:string->size
        registerMap       --dict   register name:string->number:string
        registerPrivilege --dict   register number:string->privilege:bool
        registerProfile   --dics   register number:string->profile:string

        Privilege determines whether a register is user-writable.

        Profile may be one of:
            gp (general purpose), PC (program counter), psw (status)
    """

    def __init__(self, filename):
        self.document=XmlDocument(filename)
        self.rootNode=self.document.rootNode
        self.getLanguage()
        self.getMemory()
        self.getRegisters()

    def getRecord(self):
        return self.Record

    def getLanguage(self):
        """Stores the language recognized by the machine implementation

        Reads an xml machine specification and looks for the language
        recognised by that machine.
        """
        self.Record.language=self.document.rootNode.getElementsByTagName('language')[0].attributes['name'].value.encode('ascii')

    def getMemory(self):
        """Stores a segmentation profile for the machine's memory

        Reads an xml machine specification and looks for details
        of its memory organization.
        """
        memory={}
        memoryNode=self.rootNode.getElementsByTagName('memory')[0]
        self.Record.memSize=memoryNode.attributes['size'].value.encode('ascii')
        textNode  = memoryNode.getElementsByTagName('text')[0]
        dataNode  = memoryNode.getElementsByTagName('data')[0]
        stackNode = memoryNode.getElementsByTagName('stack')[0]
        for node in [textNode, dataNode, stackNode]:
            name  = node.tagName.encode('ascii')
            start = node.attributes['start'].value.encode('ascii')
            end   = node.attributes['end'].value.encode('ascii')
            memory[name]=(start,end)
        self.Record.memory=memory

    def getRegisters(self):
        """Stores a register profile and associated data

        Reads an xml machine specification and looks for details
        of the registers.

        Generates a number:name lookup table for the use of
        the interpreter
        """
        registerValue={}
        registerSize={}
        registerMap={}
        registerPrivilege={}
        registerProfile={}
        registersNode=self.rootNode.getElementsByTagName('registers')
        registerNodeList=registersNode[0].getElementsByTagName('register')
        for register in registerNodeList:
            #walk the list of registers
            name    = register.attributes['name'].value.encode('ascii')
            number  = register.attributes['number'].value.encode('ascii')
            size    = register.attributes['size'].value.encode('ascii')
            write   = register.attributes['write'].value.encode('ascii')
            profile = register.attributes['profile'].value.encode('ascii')
            #
            #all the registers are initialized to zero
            #
            registerValue[number]     = '0x00'
            registerSize[number]      = size
            registerMap[name]         = number
            registerPrivilege[number] = bool(write)
            if profile in registerProfile.keys():
                registerProfile[profile].append(number)
            else:
                registerProfile[profile] = [number]
        #
        #set the preset register values
        #
        presetsNode=self.rootNode.getElementsByTagName('presets')
        presetNodeList=presetsNode[0].getElementsByTagName('preset')
        for preset in presetNodeList:
            number = preset.attributes['number'].value.encode('ascii')
            value  = preset.attributes['value'].value.encode('ascii')
            if number in registerValue:
                registerValue[number]=value
            else:
                raise XmlDataFormatException()
        self.Record.registerValue     = registerValue
        self.Record.registerSize      = registerSize
        self.Record.registerMap       = registerMap
        self.Record.registerPrivilege = registerPrivilege
        self.Record.registerProfile   = registerProfile




if __name__ == '__main__':
    reader=InstructionReader('../../xml/instructions.xml')
    isa=reader.getRecord()
    language=isa.language
    size=isa.size

    print "Success: read `{0}', a {1:2d}-bit ISA".format(language,int(size,16))

    #reader=MachineReader('../../xml/machine.xml')
    #machine=reader.getRecord()
    #print "Success: read `{0}' from file".format(machine.language)



"""
Copyright (C) 2011 Tom Regan <code.tregan@gmail.com>.
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
