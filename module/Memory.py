#!/usr/bin/env python
''' Memory.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-18
description: Provides memory objects
'''

class UnallignedException(Exception):
    pass

class SegmentationFaultException(Exception):
    pass




class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError




class BaseMemory(Loggable):

    def openLog(self, logger):
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

    def __init__(self, _address_space, instructions):
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

        self._address_space = _address_space
        self._byte          = 8
        self._size          = instructions.getSize()
        self._endian        = Enum(["Big"])

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

        memory_slice={}
        for i in range(end, start+1):
            if not self.in_range(i):
                return memory_slice
            try:
                memory_slice[int(i)]=self.getWord32(i)
            except:
                memory_slice[int(i)]=0
        return memory_slice


    def load_text(self, text, and_dump=True):
        """[programme:int]:list -> memory{offset:value}:dict

        Stores <programme> in sequential addresses in memory.
        """

        if and_dump == True:
            self.dumpMemory()

        offset = self.get_start('text')
        for line in text:
            if not type(line) == int and not type(line) == long:
                raise DataFormatException('loadText: got {:} expected an int{"}'.format(line,type(line)))
            if offset > self.get_end('text'):
                raise SegmentationFaultException
            self.setWord32(offset, line)
            offset = offset + 1
        self.log.buffer('loaded {0} word programme into memory'.format(len(text)))

    def reset(self):
        """... -> ...

        Clears the memory address space. Good for debugging.
        """

        self.log.buffer('memory cleared')
        self._address.clear()

    def get_word(self, offset):
        """-> value:int

        Returns the decimal value of a word in memory
        """
        #
        #expect a `key error' exception, but behave as though this was
        #a successful memory read. Return 0s.
        #
        if not self.in_range(offset):
            self.log.buffer('Segmantation violation')
            raise SegmentationFaultException
        try:
            self.log.buffer('loaded {0} from {1}'.format(bin(self._address[offset], self._size)[2:],hex(offset)))
            return self._address[offset]
        except Exception:
            self.log.buffer('loaded {0} from {1}'.format(bin(0, self._size)[2:],hex(offset)))
            return 0

    def get_byte(self, offset, value):
        pass

    def set_word(self, offset, value, endian=self._endian.Big):
        """(offset:int, value:int) -> memory{offset:value}:dict

        Inserts a word at the given memory offset
        """
        bitmap=bin(value, self._size)[2:]
        start=0
        end=self._byte
        for i in range(self._size/self._byte):
            self.set_byte(offset, int(bitmap[start:end],2))
            start=end
            end=end+self._byte
            if endian == self._endian.Big:
                offset = offset - self._byte
            else:
                offset = offset + self._byte
        self.log.buffer('stored {0} at {1}'.format(bitmap,hex(offset)))

    def set_byte(self, offset, value):
        if not self.in_range(offset):
            raise SegmentationFaultException
        self._address[offset] = value

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
