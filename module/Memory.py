#!/usr/bin/env python
''' Memory.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-18
description: Provides memory objects
'''

from lib.Interface  import *
from lib.Logger     import *
from lib.Functions  import binary as bin

class AddressingError(Exception):
    pass

class AlignmentError(Exception):
    pass

class DataFormatException(Exception):
    pass

class SegmentationFaultException(Exception):
    pass




class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError




class BaseMemory(Loggable):

    def open_log(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """

        self.log = MemoryLogger(logger)
        self.log.buffer('created {0}-Kb of {1}-byte address space'.format(str(self._address_space[1])[:-3], (self._size)/4))

    def get_memory(self):
        """-> memory:object
        Returns a reference to the newly created memory object
        """
        return self

    def add_segment(self, name, start, end):
        pass

    def get_slice(self, end=None, start=None):
        pass




class Memory(BaseMemory):
    """Provides an interface that should be used to initialize the memory.

    Usage:
        memory=Memory(_address_space=(0,2147483647),
                      text=(4194304,268435456),
                      data=(268435456,2147483647),
                      stack=(268435456,2147483647))

    This memory model is big-endian. For representations of many
    systems this will have to be extended.

    Segmentation is not currently enforced. A programme may write
    to any valid memory address.
    """

    #
    #Memory is implemented as a dict. To avoid wasted (real) memory,
    #a range is stored indicating the bounds of each segment, but
    #no space is reserved. This makes sense for 32-bit+ ISAs, and
    #spares us the embarrasment trying to malloc 4GB.
    #
    _address={}
    _segment={}

    def __init__(self, address_space, instructions):
        """Memory space:
            [_address_space]:list
            instruction:object (module.Isa.InstructionSet)

            Usage:
                memory=Memory((0,64000), instructions)
                memory.addSegment('reserved', 0, 512)
                memory.addSegment('text', 513, 1024)
                memory.addSegment('data", 1025, 64000)
                memory.addSegment('stack", 1025, 64000)

            NB. _address_space should be a list of len 2,
            start and end. The can be acquired from XmlLoader.
        """

        self._address_space = address_space
        self._addressable   = 8
        self._size          = instructions.getSize()
        self._types         = Enum(["Big", "Little"])
        self._endian        = self._types.Big

    def add_segment(self, name, start, end):
        """(name:str, start:int, end:int) -> segment{name:[start,end]:list}:dict

        Designates a new segment with implicit access controls.
        """
        #
        #It's a serious error not to receive both start and end
        #values for memory offsets. We can't go on.
        #
        if not self.in_range(start) or not self.in_range(end):
            raise Exception
        self.log.buffer("created segment `{0}'\t{1}..{2}".format(name,start,end))
        self._segment[name]=[start,end]

    def get_slice(self, end=None, start=None):
        """(end:int, start:int)->{address:int->values:int}:dict

        Returns a list of binary values stored in a range of memory.
        Meant to be used to display.

        Values will be unsorted.
        """
        if not start: start=self.get_end('stack')
        if not end:
            end = start-11
        else:
            end = start-end+1

        if start > end:
            temp  = start
            start = end
            end   = temp

        memory_slice={}
        for i in range(start, end+1):
            if not self.in_range(i):
                raise SegmentationFaultException('{:} is out of bounds'
                                 .format(hex(offset)[2:].replace('L','')))
            try:
                memory_slice[int(i)]=self.get_word(i)[1]
            except:
                memory_slice[int(i)]=0
        return memory_slice


    def load_text(self, text, and_dump=False):
        """([programme:int]:list, and_dump:bool)
                -> memory{offset:value}:dict

        Stores [programme] in sequential addresses in memory.
        """

        if and_dump == True:
            self.reset()

        offset = self.get_start('text')
        for line in text:
            if not type(line) == int and not type(line) == long:
                raise DataFormatException(
                    'loadText: got {:} expected an int{:}'
                    .format(line,type(line)))
            if offset > self.get_end('text'):
                raise SegmentationFaultException('{:} is out of bounds'
                                 .format(hex(offset)[2:].replace('L','')))
            self.set_word(offset, line, self._size)
            offset = offset + (self._size / self._addressable)
        self.log.buffer('loaded {0} word programme into memory'
                        .format(len(text)))

    def load_text_and_dump(self, text):
        """Synonymous with load_text with the dump option set"""
        self.load_text(text=text, and_dump=True)

    def get_word(self, offset, size, aligned=True):
        """(offset:int,
            size:int
            aligned:bool) -> value:int

        Returns a tuple containing address offset and
        the decimal value of a word at that location.

        Values:
            offset  -- the address in memory
            size    -- the word size to get
            aligned -- is word alligment enforced?

        Raises:
            AddressingError
            AlignmentError
        Allows:
            SegmentationFaultException
        Masks:
            KeyValue (in _get_byte)
        """
        #We want to prevent addressing violations
        if size < self._addressable:
            self.log.buffer('Addressing error: load {:}B from {:}'
                            .format(size/8, hex(offset)[2:]))
            raise AddressingError('Tried to load {:}-Bytes from {:}'
                                  .format(size/8, hex(offset)[2:]))

        #We want to prevent bad allignment
        #if aligned and int(offset) % size != 0:
        if aligned and int(offset) % (size / self._addressable) != 0:
            self.log.buffer('Alignment error: load {:}B from {:}'
                            .format(size/8, hex(offset)[2:]))
            raise AlignmentError('Tried to load {:}B from {:}'
                                 .format(size/8, hex(offset)[2:]))

        if self._endian == self._types.Little:
            offset = offset - (size/self._addressable)

        bitmap=[]
        orig_offset=offset
        start=0
        end=self._addressable

        for i in range(size/self._addressable):

            byte = self._get_byte(offset)
            bitmap[start:end] = bin(byte, self._addressable)[2:]

            if self._endian == self._types.Big:
                offset = offset + 1
            else:
                offset = offset - 1

            start=end
            end=end+self._addressable

        bitmap=''.join(bitmap)
        self.log.buffer('loaded {:} from {:}'
                        .format(bitmap,hex(orig_offset)[2:]))
        return int(bitmap, 2)


    def _get_byte(self, offset):
        #We want to prevent segmentation violations
        if not self.in_range(offset):
            self.log.buffer('Segmantation violation: {:} is out of bounds'
                            .format(hex(offset)[2:].replace('L','')))
            raise SegmentationFaultException('{:} is out of bounds'
                                 .format(hex(offset)[2:].replace('L','')))
        #Expect a `key error' exception, but behave as though this was
        #a successful memory read. Return 0.
        try:
            return self._address[offset]
        except KeyError, e:
            #We will initialize the memory to avoid future exceptions
            self._set_byte(offset, 0)
            return 0

    def set_word(self, offset, value, size, aligned=True):
        """(offset:int,
            value:int,
            size:int,
            aligned:bool) -> **memory{offset:value}:dict**

        Inserts a word at the given memory offset

        Values:
            offset  -- the address in memory
            value   -- the value to be stored
            size    -- the word size to set
            aligned -- is word alligment enforced?

        Raises:
            AddressingError
            AlignmentError
        Allows:
            SegmentationFaultException
        Masks:
            None
        """
        #We want to prevent addressing violations
        if size < self._addressable:
            self.log.buffer('Addressing error: store {:} at {:}'
                            .format(bin(value, self._size)[2:].lstrip('0'),
                                    hex(offset)[2:].replace('L','')))
            raise AddressingError('Tried to store {:} at {:}'
                                  .format(bin(value, self._size)[2:],
                                          hex(offset)[2:].replace('L','')))

        #We want to prevent bad allignment
        if aligned and int(offset) % (size / self._addressable) != 0:
            self.log.buffer('Alignment error: store {:} at {:}'
                            .format(bin(value, self._size)[2:],
                                    hex(offset)[2:].replace('L','')))
            raise AlignmentError('Tried to store {:} at {:}({:})'
                                 .format(bin(value, self._size)[2:],
                                         hex(offset)[2:].replace('L',''),
                                         int(offset) % size))

        if self._endian == self._types.Little:
            offset = offset - (size/self._addressable)

        orig_offset = offset
        bitmap=bin(value, size)[2:]
        start=0
        end=self._addressable
        for i in range(size/self._addressable):
            self._set_byte(offset, int(bitmap[start:end],2))
            start=end
            end=end+self._addressable
            if self._endian == self._types.Big:
                offset = offset + 1
            else:
                offset = offset - 1
                self.log.buffer('stored {:} at {:}'
                                .format(bitmap,hex(orig_offset)[2:]))

    def _set_byte(self, offset, value):
        #We want to prevent segmentation violations
        if not self.in_range(offset):
            self.log.buffer('Segmantation violation: {:} is out of bounds'
                            .format(hex(offset)[2:].replace('L','')))
            raise SegmentationFaultException('{:} is out of bounds'
                                 .format(hex(offset)[2:].replace('L','')))
        self._address[offset] = value

    def reset(self):
        """... -> ...

        Clears the memory address space. Good for debugging.
        """

        self.log.buffer('core dumped to null')
        self._address.clear()

    def in_range(self, address):
        """address:int -> bool"""
        return address >= self._address_space[0] and address <= self._address_space[1]

    def get_start(self, name):
        """name:str -> start:int

        Returns the start address of a segment.
        """
        return self._segment[name][0]

    def get_end(self, name):
        """name:str -> end:int

        Returns the end address of a segment.
        """
        return self._segment[name][1]
