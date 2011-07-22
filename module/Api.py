#!/usr/bin/env python
#coding=iso-8859-15
#
# Interface for simulation clients.
# file           : Api.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-01
# last modified  : 2011-07-22

from SystemCall import *

from lib.Logger import ApiLogger
from lib.Interface import *

class _Api(Loggable):
    """Base class which provides the necessary storage and initialization
    for derrived Api implementations
    """

    #
    #The Api object requires references to CPU internals so that it
    #can change its state.
    #
    _register = None
    _memory   = None
    _instruction_decoded = None

    def open_log(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """

        self.log = ApiLogger(logger)
        self.log.buffer('created an api')

    def getApiReference(self, cpu):
        """cpu:object -> api:object

        Takes a reference to a Cpu object and links the CPU and API.

        Usage:
            api = Api.getApiReference(cpu)

            (Usually within __init__ of the CPU.)
        """

        self._register = cpu.get_registers()
        self._memory   = cpu.get_memory()
        return self


class Sunray(_Api):
    """An API implementation which primarily supports the MIPS32 ISA."""

    def addRegisters(self, args, instruction_decoded):
        """args:list -> True

        Adds two registers and stores the result in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
            register[a]['value'] <-
                register[b]['value'] + register[c]['value']

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('addRegisters called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.getValue(b) + self._register.getValue(c)
        self._register.setValue(a, result)
        self.log.buffer('setting register {0} to {1}'.format(a,result))
        return True

    def addImmediate(self, args, instruction_decoded):
        """args:list -> True

        Adds a register to an immediate value and stores the result in
        a second register.

        Args:
            Args 1 and 2 should be the numbers of registers.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
             register[a]['value'] <- register[b]['value'] + c:int

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('addImmediate called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.getValue(b) + c
        self._register.setValue(a, result)
        self.log.buffer('setting register {0} to {1}'.format(a,result))
        return True


    def subRegisters(self, args, instruction_decoded):
        """args:list -> True

        Subtracts two registers and stores the result in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
            register[a]['value'] <-
                register[b]['value'] - register[c]['value']

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('subRegisters called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.getValue(b) - self._register.getValue(c)
        self._register.setValue(a, result)
        self.log.buffer('setting register {0} to {1}'.format(a,result))
        return True

    def mulRegisters(self, args, instruction_decoded):
        """args:list -> True

        Multiplies two registers and stores the product in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
            register[a]['value'] <-
                register[b]['value'] * register[c]['value']

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('mulRegisters called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.getValue(b) * self._register.getValue(c)
        self._register.setValue(a, result)
        self.log.buffer('setting register {0} to {1}'.format(a,result))
        return True

    def divRegisters(self, args, instruction_decoded):
        """args:list -> True

        Divides two registers and stores the quotient in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
            register[a]['value'] <-
                register[b]['value'] / register[c]['value']

        Returns:
            Always returns True

        Raises:
            ArithmeticError
            RegisterReferenceException
        """
        self.log.buffer('divRegisters called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        if b == 0 or c == 0:
            raise ArithmeticError
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.getValue(b) / self._register.getValue(c)
        self._register.setValue(a, result)
        self.log.buffer('setting register {0} to {1}'.format(a,result))
        return True

    def setRegister(self, args, instruction_decoded):
        """args:list -> True

        Sets the value of a register.

        Args:
            Either argument can be a register or immediate value.
            args[0]:int (target)
            args[1]:int (value)

        State changed:
            register[a]['value'] <- b:int

        Returns:
            Always returns True
        """
        self.log.buffer('setRegister called')
        #
        #This is a special case! No other instruction has
        #numerical values in the implementation.
        #
        if type(args[0]) == int:
            a = args[0]
        else:
            a = instruction_decoded[args[0]]
        if type(args[1]) == int:
            b = args[1]
        else:
            b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self._register.setValue(a, b)
        self.log.buffer('setting register {0} to {1}'.format(a,b))
        return True

    def loadWord32(self, args, instruction_decoded):
        """args:list -> True

        Loads a word from memory.

        Args:
            args[0]:int (target)
            args[1]:int (memory offset)

        State changed:
            register[a]['value'] <- memory[b]

        Returns:
            Always returns True
        """
        self.log.buffer('loadWord32 called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        offset=int(c)+self._register.getValue(int(b))
        word = self._memory.get_word(offset, 32)
        self._register.setValue(int(a), word)
        self.log.buffer('loading {:} into {:} from {:}'.format(word,a,offset))
        return True

    def storeWord32(self, args, instruction_decoded):
        """args:list -> True

        Loads a word from memory.

        Args:
            args[0]:int (register)
            args[1]:int (target)

        State changed:
            memory[b] <- register[a]['value']

        Returns:
            Always returns True
        """
        self.log.buffer('storeWord32 called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        c = instruction_decoded[args[2]]
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        value=self._register.getValue(int(a))
        offset=int(c)+self._register.getValue(int(b))
        self._memory.set_word(offset, value, 32)
        self.log.buffer('storing {:} in {:}'.format(value,hex(offset)))
        return True

    def testEqual(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a and b are equal.
        """
        self.log.buffer('testEqual called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) == self._register.getValue(b)))
        return self._register.getValue(a) == self._register.getValue(b)

    def testNotEqual(self, args, instruction_decoded):
        """args:list -> bool

        Returns false if a and b are equal.
        """
        self.log.buffer('testNotEqual called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) != self._register.getValue(b)))
        return self._register.getValue(a) != self._register.getValue(b)

    def testLess(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a is less than b.
        """
        self.log.buffer('testLess called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) < self._register.getValue(b)))
        return self._register.getValue(a) < self._register.getValue(b)

    def testLessImmediate(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a is less than b.
        """
        self.log.buffer('testLessImmediate called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) < b))
        return self._register.getValue(a) < b

    def testGreater(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a > b.
        """
        self.log.buffer('testGreater called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) > self._register.getValue(b)))
        return self._register.getValue(a) > self._register.getValue(b)

    def testGreaterOrEqual(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a >= b.
        """
        self.log.buffer('testGreaterOrEqual called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) >= self._register.getValue(b)))
        return self._register.getValue(a) >= self._register.getValue(b)

    def testGreaterImmediate(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a > b.
        """
        self.log.buffer('testGreaterImmediate called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) > b))
        return self._register.getValue(a) > b

    def testGreaterOrEqualImmediate(self, args, instruction_decoded):
        """args:list -> bool

        Returns true if a >= b.
        """
        self.log.buffer('testGreaterOrEqualImmediate called')
        a = instruction_decoded[args[0]]
        b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.getValue(a) >= b))
        return self._register.getValue(a) >= b

    def branchAbsolute(self, args, instruction_decoded):
        """args:list, instruction_decoded:dict -> True"""
        self.log.buffer('branchAbsolute called')
        a=instruction_decoded[args[0]]
        pc=self._register.getPc()
        self._register.setValue(pc, a)
        return True

    def branchRelative(self, args, instruction_decoded):
        """args:list, instruction_decoded:dict -> True
        Takes an optional delay if control will return
        to a distant place"""
        self.log.buffer('branchRelative called')
        a=instruction_decoded[args[0]]
        self.log.buffer('args 0:{0}'.format(a))
        # add branch delay
        if len(args) > 1:
            b=args[1]
            a = a + b
        pc = self._register.getPc()
        value = self._register.getValue(pc)
        self.log.buffer('pc is {:}'.format(hex(value)))
        word_space = self._memory.get_word_spacing()
        self.log.buffer('word-space is {:}'.format(word_space))
        a = a * word_space
        self.log.buffer('increment is {:}'.format(a))
        a = value + a
        self._register.setValue(pc, a)
        return True

    def incrementPc(self, args, instruction_decoded):
        """args:list -> True"""
        self.log.buffer('incrementPc called')
        a=instruction_decoded[args[0]]
        pc=self._register.getPc()
        value=self._register.getValue(pc)+a
        self._register.setValue(pc, value)
        return True

    def doNothing(self, args, instruction_decoded):
        """args:list -> True"""
        self.log.buffer('doNothing called')
        return True

    def systemCall(self, args, instruction_decoded):
        """args:list -> True"""
        self.log.buffer('systemCall called')
        system_call = SystemCall()
        a=args[0]
        self.log.buffer('args 0:{0}'.format(a))
        result = self._register.getValue(a)
        system_call.service(result)
        return True
