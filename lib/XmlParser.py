#!/usr/bin/env python
#
# XML Parser.
# file           : XmlParser.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-20
# last modified  : 2011-07-22


from xml.dom.minidom import parse
from Functions       import asciify




class XmlDataFormatException(Exception):
    """Xml file is not valid """
    pass




class XmlDocument(object):
    """Provides a basic interface to an XML file"""
    def __init__(self, filename):
        self._xml_doc   = parse(filename)
        self._root_node = self._xml_doc.documentElement

class XmlReader(object):
    """Provides storage for derrived classes """
    _data={}

    def __del__(self):
        self._data.clear()

class InstructionReader(XmlReader):
    """A class to parse an instruction.xsd-validated isa specification"""

    def __init__(self, filename):
        self._document=XmlDocument(filename)
        self._root_node=self._document._root_node
        self._parse_root()
        self._parse_formats()
        self._parse_assembler()
        self._parse_instructions()

        self.data = self._data

    def _parse_root(self):
        language = asciify(self._root_node.attributes['language'].value)
        size     = asciify(self._root_node.attributes['size'].value)
        api      = asciify(self._root_node.attributes['api'].value)
        self._data['language'] = language
        self._data['size']     = int(size, 16)
        self._data['api']      = api

    def _parse_formats(self):
        data=[]
        f_root = self._root_node.getElementsByTagName('formats')[0]
        formats = f_root.getElementsByTagName('format')
        for format in formats:
            f_type = asciify(format.attributes['type'].value)
            f_size = int(asciify(format.attributes['size'].value), 16)
            fields = format.getElementsByTagName('field')
            f_data=[]
            for field in fields:
                fd_name  = asciify(field.attributes['name'].value)
                fd_start = int(asciify(field.attributes['start'].value), 16)
                fd_end   = int(asciify(field.attributes['end'].value), 16)
                f_data.append((fd_name, fd_start, fd_end))
            data.append((f_type, f_size, tuple(f_data)))

        self._data['formats'] = tuple(data)

    def _parse_instructions(self):
        data=[]
        instructions=self._root_node.getElementsByTagName('instruction')
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
                im_name = asciify(method.attributes['name'].value)
                im_args = asciify(method.attributes['args'].value)
                #TODO
                #replace below with lambda
                #
                for i in range(len(im_args)):
                    if im_args[i][:2] == '0x':
                        im_args[i] = int(im_args[i],16)
            i_implementation.append(tuple((im_name,
                                           tuple(im_args.split()))))

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

    def _parse_assembler(self):
        """{ name:<string> : pattern:<string> } -> assembler_syntax

        Reads an XML instruction specification and looks for the
        assembler syntax.
        """

        assembler = self._root_node.getElementsByTagName('assembler')[0]
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

    def get_data(self):
        return self._data




class MachineReader(XmlReader):
    """A class to parse a machine.xsd-validated machine specification"""

    _language=None
    _address_space=None
    _memory={}
    _registers={}
    _register_mappings={}

    def __init__(self, filename):
        self._document=XmlDocument(filename)
        self._root_node=self._document._root_node
        self._parse_root()
        self._parse_language()
        self._parse_memory()
        self._parse_registers()
        self._parse_pipeline()

        self.data = self._data

    def _parse_root(self):
        name = asciify(self._root_node.attributes['name'].value)
        self._data['name'] = name

    def _parse_language(self):
        try:
            language = self._root_node.getElementsByTagName('language')[0]
            l_name = asciify(language.attributes['name'].value)
            self._data['language'] = l_name
        except Exception, e:
            raise XmlDataFormatException(e.message)

    def _parse_memory(self):
        """Stores a segmentation profile for the machine's memory

        Reads an xml machine specification and looks for details
        of its memory organization.
        """
        memory=[]

        try:
            memory_node=self._root_node.getElementsByTagName('memory')[0]
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
        except Exception, e:
            raise XmlDataFormatException(e.message)
        #TODO
        #address space is currently hard-coded to begin at 0x00.
        #this is just a marker for future refactoring
        #
        self._data['memory']=tuple(memory)

    def _parse_registers(self):
        registers=[]

        registers_node=self._root_node.getElementsByTagName('registers')
        register_node_list=registers_node[0].getElementsByTagName('register')
        for register in register_node_list:
            name    = asciify(register.attributes['name'].value)
            number  = int(asciify(register.attributes['number'].value), 16)
            size    = int(asciify(register.attributes['size'].value), 16)
            write   = asciify(register.attributes['write'].value)
            write = (write == 'True' and True or False)
            profile = asciify(register.attributes['profile'].value)
            visible = asciify(register.attributes['visible'].value)
            visible = (visible == 'True' and True or False)
            #prepared to be nice and leniant for this one
            preset  = 0
            try:
                preset  = int(asciify(register.attributes['preset'].value), 16)
            except:
                pass

            registers.append((name, number, size, write, profile,
                              visible, preset))

        self._data['registers'] = tuple(registers)

    def _parse_pipeline(self):
        try:
            pipeline = self._root_node.getElementsByTagName('pipeline')[0]
            stages   = pipeline.getElementsByTagName('stage')

            pipeline_stages = []
            for stage in stages:
                name = asciify(stage.attributes['name'].value)
                pipeline_stages.append(name)
        except Exception, e:
            raise XmlDataFormatException(e.message)
        self._data['pipeline'] = tuple(pipeline_stages)


    def get_data(self):
        return self._data




if __name__ == '__main__':
    reader=InstructionReader('../config/instructions.xml')
    #print reader.data['instructions'][0]
    del reader

    reader=MachineReader('../config/machine.xml')
    print(reader.data)
    del reader
