#!/usr/bin/env python
#
# Hardware Components.
# file           : System.py
# author         : Tom Regan (code.tregan@gmail.com)
# since          : 2011-06-27
# last modified  : 2011-07-22
#
# DEPRECATED
#


import Isa

from copy import deepcopy
from lib.Logger   import CpuLogger, MemoryLogger, RegisterLogger
from lib.Functions import binary as bin
from lib.Interface import *

class RegisterReferenceException(Exception):
    pass

class OpCodeNotInMemoryException(Exception):
    pass

class SegmentationFaultException(Exception):
    pass

class DataFormatException(Exception):
    """Signals a memory load contained non integer data"""
    pass

class Machine(object):
    """Wraps the simulation elements.

    Usage:
        machine=Machine()
        machine.addCpu(processor)
        machine.cpu[0].cycle()
    """

    cpu=[]

    def addCpu(self, cpu):
        if not isinstance(cpu, Cpu()):
            raise Exception
        self.cpu.append(cpu)

#
#Interface and implementation for the memory below
#

class Memory(Loggable):
    """Provides an interface that should be used to initialize the memory.

    Usage:
        memory=Memory(address_space=(0,2147483647),
                      text=(4194304,268435456),
                      data=(268435456,2147483647),
                      stack=(268435456,2147483647))

    This memory model is big-endian. For representations of many
    systems this will have to be extended.

    Segmentation is not currently enforced. A program may write
    to any valid memory address.
    """

    #
    #Memory is implemented as a dict. To avoid wasted (real) memory,
    #a range is stored indicating the bounds of each segment, but
    #no space is reserved. This makes sense for 32-bit+ ISAs, and
    #spares us the embarrasment trying to malloc 4GB.
    #
    address={}
    _segment={}

    base_16 = 16
    base_2  =  2

    def __init__(self, address_space, instructions):
        """Memory space:
            [address_space]:list
            instruction:object (module.Isa.InstructionSet)

            Usage:
                memory=Memory((0,64000), instructions)
                memory.addSegment('reserved', 0, 512)
                memory.addSegment('text', 513, 1024)
                memory.addSegment('data", 1025, 64000)
                memory.addSegment('stack", 1025, 64000)

            NB. address_space should be a list of len 2,
            start and end. The can be acquired from XmlLoader.
        """

        self.address_space = address_space
        self._size         = instructions.getSize()
        assert(type(self._size) == int)

    def openLog(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """

        self.log = MemoryLogger(logger)
        self.log.buffer('created {0}-Kb of {1}-byte address space'.format(str(self.address_space[1])[:-3], (self._size)/4))

    def get_slice(self, end=None, start=None):
        """(end:int, start:int)->{address:int->values:int}:dict

        Returns a list of binary values stored in a range of memory.
        Meant to be used to display.

        Values will be unsorted.
        """
        if not start: start=self.getEnd('stack')
        if not end:
            end = start-11
        else:
            end = start-end+1

        memory_slice={}
        for i in range(end, start+1):
            if not self.isInRange(i):
                return memory_slice
            try:
                memory_slice[int(i)]=self.getWord32(i)
            except:
                memory_slice[int(i)]=0
        return memory_slice


    def loadText(self, text, and_dump=True):
        """[program:int]:list -> memory{offset:value}:dict

        Stores <program> in sequential addresses in memory.
        """

        if and_dump == True:
            self.dumpMemory()

        offset = self.getStart('text')
        for line in text:
            if not type(line) == int and not type(line) == long:
                raise DataFormatException('loadText: got {:} expected an int{"}'.format(line,type(line)))
            if offset > self.getEnd('text'):
                raise SegmentationFaultException
            self.setWord32(offset, line)
            offset = offset + 1
        self.log.buffer('loaded {0} word program into memory'.format(len(text)))

    def dumpMemory(self):
        """... -> ...

        Clears the memory address space. Good for debugging.
        """

        self.log.buffer('memory cleared')
        self.address.clear()

    def getWord32(self, offset):
        """-> value:int

        Returns the decimal value of a word in memory
        """
        #
        #expect a `key error' exception, but behave as though this was
        #a successful memory read. Return 0s.
        #
        if not self.isInRange(offset):
            self.log.buffer('Segmantation violation')
            raise SegmentationFaultException
        try:
            self.log.buffer('loaded {0} from {1}'.format(bin(self.address[offset], self._size)[2:],hex(offset)))
            return self.address[offset]
        except Exception:
            self.log.buffer('loaded {0} from {1}'.format(bin(0, self._size)[2:],hex(offset)))
            return 0

    def getHalfWord32(self, offset):
        """-> value:str

        Returns:
            An integer representation of the first two bytes of
            a 4-byte word (or 0s if empty).

        Raises:
            SegmentationFaultException
        """
        if not self.isInRange(offset):
            raise SegmentationFaultException
        try:
            size = self._size/2
            value = bin(self.address[offset], self._size)[2:]
            value = value[:size]
            value = int(value, self.base_2)
            return value
        except Exception:
            return 0

    def getByte32(self, offset):
        """-> value:str

        Returns:
            An integer representation of the first byte of
            a 4-byte word (or 0s if empty).

        Raises:
            SegmentationFaultException
        """
        if not self.isInRange(offset):
            raise SegmentationFaultException
        try:
            size = self._size/4
            value = bin(self.address[offset], self._size)[2:]
            value = value[:size]
            value = int(value,self.base_2)
            return value
        except Exception:
            return 0

    def setWord32(self, offset, value):
        """(offset:int, value:int) -> memory{offset:value}:dict

        Inserts a 32-bit word at the given memory offset
        """
        if not self.isInRange(offset):
            raise SegmentationFaultException
        self.address[offset] = value
        self.log.buffer('stored {0} at {1}'.format(bin(value, self._size)[2:],hex(offset)))

    def setHalfWord32(self, offset, value):
        """(offset:int, value:int) -> memory{offset:value}:dict

        Inserts a 16-bit word at the given memory offset
        """
        if not self.isInRange(offset):
            raise SegmentationFaultException
        size = self._size/2
        value = bin(value, size)
        value = value + '0'*(size)
        value = int(value, self.base_2)
        self.address[offset] = value

    def setByte32(self, offset, value):
        """(offset:int, value:int) -> memory{offset:value}:dict

        Inserts a byte word at the given memory offset
        """
        if not self.isInRange(offset):
            raise SegmentationFaultException
        size = self._size/4
        value = bin(value, size)
        value = value + '0'*(size*3)
        value = int(value, self.base_2)
        self.address[offset] = value

    def isInRange(self, address):
        """address:int -> bool"""
        return address >= self.address_space[0] and address <= self.address_space[1]

    def addSegment(self, name, start, end):
        """(name:str, start:int, end:int) -> segment{name:[start,end]:list}:dict

        Designates a new segment with implicit access controls.
        """
        #
        #It's a serious error not to receive both start and end
        #values for memory offsets. We can't go on.
        #
        if not self.isInRange(start) or not self.isInRange(end):
            raise Exception
        self.log.buffer("created segment `{0}'\t{1}..{2}".format(name,start,end))
        self._segment[name]=[start,end]

    def getStart(self, name):
        """name:str -> start:int

        Returns the start address of a segment.
        """
        return self._segment[name][0]

    def getEnd(self, name):
        """name:str -> end:int

        Returns the end address of a segment.
        """
        return self._segment[name][1]

    def getMemory(self):
        """-> memory:object
        Returns a reference to the newly created memory object
        """
        return self

#
#Registers interface and implementation below
#

class Registers(Loggable):
    """Provides an interface that should be used to build a set of registers

    Usage:
        registers=Registers()
        registers.addRegister(number=0, value=2147483647, size=32,
                              profile='gp', privilege=True)
        registers.removeRegister(0)
    """

    _registers={}
    _registers_iv={}
    _name_number={}
    _number_name={}

    def open_log(self, logger):
        self.log = RegisterLogger(logger)
        self.log.buffer('created registers')

    def addRegister(self, number, value, size, profile, privilege):
        """(number:int, value:int, size:int, profile:str, privilege:bool)
            -> registers{register[number]:{value,size,profile,provilege}:dict

        Adds a register.
        """

        self._registers[number]={}
        self._registers[number]['value']     = value
        self._registers[number]['size']      = size
        self._registers[number]['profile']   = profile
        self._registers[number]['privilege'] = privilege
        self.log.buffer('added register: {:>2} {:>12} {:} {:>3} {:}'
                        .format(number, value, size, profile, privilege))
        self._registers_iv = deepcopy(self._registers)

    def addRegisterMapping(self, name, number):
        """(name:str, number:int) -> register{name:number}:dict

        Creates a map of names to registers which can be used to
        assist decoding assembly instructions.
        """

        self._name_number[name]=number
        self._number_name[number]=name
        self.log.buffer("added mapping: {:} <-> {:}".format(name, number))

    def removeRegister(self, number):
        """number:int -> ...
        Deletes a register.
        """

        del self._registers[number]

    def setValue(self, number, value):
        """number:int -> ...
        Stores a value in a register.
        """
        if number not in self.keys():
            return
        name = self._number_name[number]
        self.log.buffer("setting {:} to {:}".format(name, hex(value)))
        self._registers[number]['value']=value

    def getValue(self, number):
        """number:int -> number:int
        Returns the value stored in a register.
        """
        if number not in self.keys():
            return
        return self._registers[number]['value']

    def increment(self, number, amount=1):
        """(number:int, amount=1:int) -> ...
        Increases the value in a register
        """
        name = self._number_name[number]
        self.log.buffer("adding {:} to {:}".format(amount, name))
        self._registers[number]['value'] = self._registers[number]['value']+amount
        self.log.buffer("new value is {:}"
                        .format(hex(self._registers[number]['value'])))

    def getPc(self):
        """-> register:int
        Returns the number of the register with the program counter.
        """
        return map(lambda x: x['profile'] == 'pc',
                 self._registers.values()).index(True)

    def reset(self):
        """Resets all registers to beginning values"""
        self.log.buffer("clearing register values")
        self._registers = deepcopy(self._registers_iv)

    def keys(self):
        return self._registers.keys()

    def values(self):
        values={}
        for register in self._registers:
            values[register]=self._registers[register]['value']
        return values

    def getRegisters(self):
        """... -> registers:object

        Returns a reference to register object.
        """

        return self

    def getRegisterMappings(self):
        """... -> registers{name:str->number:int}:dict

        Returns a dict of register mappings.
        """
        return self._name_number

    def get_number_name_mappings(self):
        """--- -> registers{number:int->name:str}:dict
        Returns a dict of register mappings.
        """
        return self._number_name



#
#Interface and implementation for the CPU below
#

class Cpu(Loggable, UpdateBroadcaster):
    """Wraps data objects and provides an API for running the simulation.

    """

    _instruction_raw=None          #a binary representation of the instruction
                                   #emulates the instruction cache of a processor
    _instruction_name=None         #identifier of the current instruction
    _instruction_decoded={}        #{field : value}
    _instruction_implementation={} #{instruction name : (method : [args])}
    _instruction_signatures={}     #{instruction name : {field : value}}
    _instruction_formats={}        #{instruction name : format name}
    _format_fields={}              #{format name : {field : [start, end]}}

    _register={}                   #{number : {field : value}}
    _memory={}                     #{address : value}

    #
    #Offset will be specified by the instruction-set as the offset
    #a PC jump will make. This is not properly implemented as of
    #2011-06-27
    #
    _offset=1

    def __init__(self, registers, memory, api, instructions):
        """Initialises register and memory values for a Cpu

        registers:object
        memory:object
        api:object
        instructions:object

        Usage:
            cpu=Cpu(registers, memory, api, instructions)
        """
        #
        #Memory, registers and an API can be loaded from
        #objects passed during initialization.
        #
        self._memory   = memory.getMemory()
        self._register = registers.getRegisters()
        self._api      = api.getApiReference(self)
        #
        #The instruction set values can be loaded from
        #the instructions object
        #
        self._size                       = instructions.getSize()
        self._instruction_signatures     = instructions.getSignatures()
        self._format_fields              = instructions.getFormatProperties()
        self._instruction_formats        = instructions.getFormatMapping()
        self._instruction_implementation = instructions.getImplementation()

        #
        #The PC is identified by its `profile' value
        #
        self._pc = self._register.getPc()

    def _broadcast(self):
        registers = self.getRegisters()
        memory    = self.getMemory()
        map(lambda x:x.update(registers=registers, memory=memory), self._listeners)

    def openLog(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """

        self.log = CpuLogger(logger)
        self.log.buffer('created a cpu')
        self.log.buffer("program counter is register {0}".format(hex(self._pc)))

    #def passCommandToLogger(self, command):
    #    """command -> log.<command>()

    #    Allows outside objects to control the log.

    #    Usage:
    #        Primarily designed to delegate flushing the log
    #        to make syncing easier.
    #        cpu.passCommandToLogger('flush')
    #    """

    #    if super(Cpu,self).passCommandToLogger(command):
    #        call = getattr(self.log, command)
    #        call()

    def cycle(self):
        """Wraps the simple fetch->decode->execute pipeline"""
        self.log.buffer('beginning a cycle')
        instructions=[]
        self._fetch()
        self._decode()
        self._execute()
        self._broadcast()
        self.log.buffer('completing a cycle')

    def _fetch(self):
        """Gets an instruction from memory and stores it internally"""

        self.log.buffer('entering fetch stage')
        offset = self._register.getValue(self._pc)
        self.log.buffer('program counter value is {0}'.format(hex(offset)))
        instruction = self._memory.getWord32(offset)
        instruction = bin(instruction, self._size)[2:]
        self.log.buffer('fetched {0}'.format(instruction))
        self._instruction_raw = instruction
        self.log.buffer('leaving fetch stage')
        self._register.increment(self._pc)

    def _decode(self):
        """Decodes the current instruction and stores data internally"""

        self.log.buffer('entering decode stage')
        instruction_name = None
        signature_format = None
        #
        #Each instruction has an identifying signature
        #instruction_signatures: {instruction name : {field : value}}
        #
        signatures=self._instruction_signatures
        for signature in signatures:
            #
            #We can compare this to sliced data from the raw instruction
            #instruction_formats: {instruction name : format name}
            #format_fields:       {format name : {field : [start, end]}}
            #
            match={}
            signature_format=self._instruction_formats[signature]
            signature_fields=signatures[signature].keys()
            for field in signature_fields:
                start = self._format_fields[signature_format][field][0]
                end   = self._format_fields[signature_format][field][1]+1
                match[field] = int(self._instruction_raw[start:end], 2)

            if signatures[signature] == match:
                instruction_name=signature
                break

        self.log.buffer("decoded `{0}' instruction".format(instruction_name))
        if not instruction_name in self._instruction_implementation.keys():
            raise OpCodeNotInMemoryException
        self.log.buffer("found `{0}' in instruction set".format(instruction_name))
        self._instruction_name=instruction_name

        #
        #The format_fields map has data we can use to slice the raw
        #instruction. We store the result in `instruction_decoded'.
        #instruction_decoded: {field : value}
        #instruction_formats: {instruction name : format name}
        #format_fields:       {format name : {field : [start, end]}}
        #
        instruction_fields=self._format_fields[signature_format].keys()
        for field in instruction_fields:
            start = self._format_fields[signature_format][field][0]
            end   = self._format_fields[signature_format][field][1]+1
            value = int(self._instruction_raw[start:end], 2)
            self._instruction_decoded[field]=value
        self.log.buffer("hashed `{0}' instruction".format(instruction_name))
        self.log.buffer('leaving decode stage')

    def _execute(self):
        """Executes the instruction and changes state"""

        self.log.buffer('entering execute stage')
        #
        #Instructions have associated lists of API calls
        #instruction_implementation: {instruction name : [(method : [args])]}
        #ie. a list containing method names with lists of args
        #
        instruction_name = self._instruction_name
        implementation   = self._instruction_implementation[instruction_name]
        blocked          = False
        #
        #implementation: []
        #method:         ('',[])+
        #
        for method in implementation:
            #
            #if the last call blocked, we're meant to skip the
            #following instruction
            #
            if blocked:
                self.log.buffer('skipping an API call')
                blocked = False
                continue
            call = getattr(self._api, method[0])
            args = method[1]
            #
            #Two things happen here: we call the method and check wether it is a
            #blocking call: blocking calls include setLess-type instructions
            #which may fail and cause the next instruction to be skipped.
            #
            self.log.buffer("calling {0} with {1}".format(call.__name__, args))
            blocked = call(args, self._instruction_decoded)
        self._instruction_decoded.clear()
        self.log.buffer('instruction slot cleared')
        self.log.buffer('leaving execute stage')

    def getRegisters(self):
        """-> registers:object

        Returns a reference to the registers associated with the CPU
        """
        return self._register

    def getMemory(self):
        """-> memory:object

        Returns a reference to the memory associated with the CPU
        """
        return self._memory




if __name__ == '__main__':
    import unittest
    import Api

    from lib.Logger import Logger

    class TestRegisters(unittest.TestCase):

        def setUp(self):
            self.registers = Registers()

        def testAddRegister(self):
            self.registers.addRegister(0, 0, 32, 'gp', True)
            self.registers.addRegister(1, 0, 32, 'gp', True)
            self.registers.addRegister(2, 0, 32, 'gp', True)
            self.registers.addRegister(3, 300, 32, 'pc', True)

            self.assertEquals({'value':0,'size':32,'profile':'gp','privilege':True},
                              self.registers._registers[0])

        def testRemoveRegister(self):
            self.registers.addRegister(0, 0, 32, 'gp', True)
            self.registers.addRegister(1, 0, 32, 'gp', True)
            self.assertTrue(self.registers._registers.has_key(1))
            self.registers.removeRegister(1)
            self.assertFalse(self.registers._registers.has_key(1))

    tests = unittest.TestLoader().loadTestsFromTestCase(TestRegisters)
    unittest.TextTestRunner(verbosity=2).run(tests)

    class TestMemory(unittest.TestCase):

        def setUp(self):
            self._size=32
            instructions=Isa.InstructionSet('MIPS_I', 32)
            self.memory = Memory(address_space=(0,1000), instructions=instructions)
            self.memory.addSegment('stack', 301, 1000)
            self.memory.addSegment('data', 301, 1000)
            self.memory.addSegment('text', 0, 300)
            logger = Logger('unittest.log')
            self.memory.openLog(logger)

        def tearDown(self):
            self.memory.log.flush()

        def testMemoryInitialization(self):
            self.assertEquals(self.memory.address_space, (0,1000) )
            self.assertEquals(self.memory._segment['stack'], [301,1000] )
            self.assertEquals(self.memory._segment['data'], [301,1000] )
            self.assertEquals(self.memory._segment['text'], [0,300] )

        def testSetAndGetFourByteWord(self):
            value = int('0x7fffffff',16)
            self.memory.setWord32(1000, value)
            self.assertEquals(value, self.memory.address[1000])
            stored = self.memory.getWord32(1000)
            self.assertEqual(stored, value)

        def testSetAndGetTwoByteWord(self):
            value = int('0x7fffffff',16)
            self.memory.setWord32(1000, value)
            self.assertEquals(value, self.memory.address[1000])
            value = bin(value, self._size)[2:]
            value = value[:16]
            value = int(value,2)
            stored = self.memory.getHalfWord32(1000)
            self.assertEqual(stored, value)

            value = 1
            self.memory.setHalfWord32(999, value)
            value = value*2**16
            stored = self.memory.getWord32(999)
            self.assertEqual(stored, value)

        def testSetAndGetByte(self):
            value = int('0x7fffffff',16)
            self.memory.setWord32(1000, value)
            self.assertEquals(value, self.memory.address[1000])
            value = bin(value, self._size)[2:]
            value = value[:8]
            value = int(value,2)
            stored = self.memory.getByte32(1000)
            self.assertEqual(stored, value)

            value = 1
            self.memory.setByte32(1000, value)
            value = value*2**24
            #stored = self.memory.getByte32(1000)
            stored = self.memory.getWord32(1000)
            self.assertEqual(stored, value)

    tests = unittest.TestLoader().loadTestsFromTestCase(TestMemory)
    unittest.TextTestRunner(verbosity=2).run(tests)

    class TestCpu(unittest.TestCase):

        def setUp(self):

            logger=Logger('unittest.log')

            #
            #Add some registers
            #
            registers = Registers()
            registers.addRegister(0, 0, 32, 'gp', True)
            registers.addRegister(1, 0, 32, 'gp', True)
            registers.addRegister(2, 0, 32, 'gp', True)
            registers.addRegister(3, 0, 32, 'pc', True)

            #
            #Add an API
            #
            api = Api.Sunray()

            #
            #Add an instruction set
            #
            instructions=Isa.InstructionSet('MIPS_I', 32)
            instructions.addSignature('add', {'op':0,'fn':32})
            instructions.addSignature('sub', {'op':0,'fn':40})
            instructions.addSignature('slti', {'op':10})
            instructions.addFormatProperty('i', {'op':[0,5],'im':[16,31],'rs':[6,10],'rt':[11,15]})
            instructions.addFormatProperty('r', {'op':[0,5],'fn':[26,31],'rs':[6,10],'rt':[11,15],'rd':[16,20],'sa':[21,25]})
            instructions.addFormatMapping('add', 'r')
            instructions.addFormatMapping('sub', 'r')
            instructions.addFormatMapping('slti', 'i')
            instructions.addImplementation('add', [('addRegisters',['rd','rs','rt'])])
            instructions.addImplementation('sub', [('subRegisters',['rd','rs','rt'])])
            instructions.addImplementation('slti', [('testLessImmediate',['rs','im']),('setRegister',['rt',1]),('testGreaterImmediate',['rs','im']),('setRegister',['rt',0])])

            #
            #Add some address space
            #
            memory = Memory(address_space=(0,1000), instructions=instructions)

            memory.addSegment('stack', 301, 1000)
            memory.addSegment('data', 301, 1000)
            memory.addSegment('text', 0, 300)

            memory.openLog(logger)

            #
            #Pass them all to a processor
            #
            self.processor=Cpu(registers=registers, memory=memory, api=api, instructions=instructions)

            self.processor.openLog(logger)

        def tearDown(self):
            self.processor._memory.dumpMemory()
            self.processor.log.flush()


        def testFetchGetsInstructionFromMemory(self):

            iset='00000000000000000000000000100000'
            #
            #The program counter has the value `300'
            #
            self.processor._memory.setWord32(0, int(iset,2))
            pcou=self.processor._register.getValue(3)
            #pcou=self.processor._register[3]['value']
            self.assertEquals(pcou, 0)
            #
            #_fetch puts a 32-bit binary word into _instruction_raw
            #from the top of the text segment
            #
            self.processor._fetch()
            iraw=self.processor._instruction_raw
            #The representation in memory is decimal
            self.assertEquals(int(iset,2), self.processor._memory.getWord32(0))
            #The raw instruction is binary
            self.assertEquals(iset, iraw)
            #
            #The pc has incremented
            #
            pcou=self.processor._register.getValue(3)
            #pcou=self.processor._register[3]['value']
            self.assertEquals(pcou, 1)

        def testDecodeSetsInstructionName(self):

            self.processor._instruction_raw = '00000000000000000000000000100000'

            self.processor._decode()
            self.assertEqual('add', self.processor._instruction_name)

        def testDecodeSetsInstructionFields(self):

            self.processor._instruction_raw = '00000000001000100001100100101000'

            good_values={}
            good_values['op']=0
            good_values['rs']=1
            good_values['rt']=2
            good_values['rd']=3
            good_values['sa']=4
            good_values['fn']=40

            self.processor._decode()
            self.assertEquals(good_values, self.processor._instruction_decoded)

        def testDecodeFailsToIdUnknownInstruction(self):

            self.processor._instruction_raw = '11111100000000000000000000100000'

            self.assertEquals(None, self.processor._instruction_name)
            self.assertEquals({}, self.processor._instruction_decoded)

        def testExecuteInstructionChangesState(self):

            #
            #Add R1 and R2 and store the result in R0
            #(R1 = 2, R2 = 2)
            #
            iset = '000000' + '00001' + '00010' + '00000' + '00000' + '100000'
            self.processor._register.setValue(1,2)
            self.processor._register.setValue(2,3)
            #self.processor._register[1]['value'] = 2
            #self.processor._register[2]['value'] = 3

            self.processor._memory.loadText([int(iset,2)])
            self.processor.cycle()

            #result = self.processor._register[0]['value']
            result = self.processor._register.getValue(0)
            self.assertEquals(result, 5)

        def testBlockingCall(self):
            i1 = '001010' + '00001' + '00000' + '0000000000000010'
            i1_val=int(i1,2)
            program=[i1_val]
            #self.processor._register[1]['value'] = 16
            self.processor._register.setValue(1, 16)
            self.processor._memory.loadText(program)
            self.processor.cycle()
            #result = self.processor._register[0]['value']
            result = self.processor._register.getValue(0)
            self.assertEqual(result, 1)

        def testCpuHaltsInAnHorrificFashion(self):
            #
            #Execute a cycle with no instruction
            #(identical to trying to execute a nonsense instruction)
            #
            self.assertRaises(OpCodeNotInMemoryException, self.processor.cycle)

        #def testGetToTheBottomOfThis(self):
        #    """The ids of two objects which are expected to be the
        #    same seem to differ.
        #    """
        #    a=self.processor._instruction_decoded
        #    b=self.processor._api._instruction_decoded
        #    a['op']=1
        #    self.assertEquals(a, b)

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCpu)
    unittest.TextTestRunner(verbosity=2).run(tests)

    #processor=Cpu()
    #processor._instruction_raw = '00000000001000100001100100101000'
    #processor._instruction_signatures['add']={'op':0,'fn':32}
    #processor._instruction_signatures['sub']={'op':0,'fn':40}
    #processor._instruction_formats={'add':'r','sub':'r'}
    #processor._format_fields = {'r':{'op':[0,5],'fn':[26,31],'rs':[6,10],'rt':[11,15],'rd':[16,20],'sa':[21,25]}}
    #processor._decode()
    #print processor._instruction_decoded
    #args=['rs','rt','rd']
    #processor.addRegisters(args)




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
