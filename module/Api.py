#!/usr/bin/env python
#coding=iso-8859-15
#
# Interface for simulation clients.
# file           : Api.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-01
# last modified  : 2011-08-04
#     2011-08-17 : Added _decode_register_reference method

# TODO: addRegistersUnsigned. (2011-08-18)

from SystemCall    import SystemCall
from Logger        import ApiLogger
from Interface     import LoggerClient
from lib.Functions import integer as int
from lib.Functions import binary as bin

class RegisterReferenceException(Exception):
    pass

class BaseApi(LoggerClient):
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
        self.log.buffer("created an api, `{:}'"
                        .format(self.__class__.__name__))

    def get_api_reference(self, cpu):
        """cpu:object -> api:object

        Takes a reference to a Cpu object and links the CPU and API.

        Usage:
            api = Api.get_api_reference(cpu)

            (Usually within __init__ of the CPU.)
        """

        self._register = cpu.get_registers()
        self._memory   = cpu.get_memory()
        return self


class Sunray(BaseApi):
    """An API implementation which primarily supports the MIPS32 ISA."""

    def _decode_register_reference(self, value, instruction_decoded):
        try:
            # Assume we are looking at an instruction that has
            # a register number encoded in some field at index
            value = int(instruction_decoded[value], 2)
        except: pass
        # Assume it is an integer value
        return value

    def addRegisters(self, args, instruction_decoded, **named_args):
        """Adds two registers and stores the result in a third.

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
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        c = self._decode_register_reference(args[2], instruction_decoded)
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        b_size = self._register.get_size(b)
        c_size = self._register.get_size(c)
        # We want 2's comp values for b and c...
        bin_bvalue = bin(self._register.get_value(b), size=b_size)
        bin_cvalue = bin(self._register.get_value(c), size=c_size)
        bvalue = int(bin_bvalue[2:], 2, signed=True)
        cvalue = int(bin_cvalue[2:], 2, signed=True)
        result = bvalue + cvalue
        # ... and we want to store the result as a signed number.
        a_size = self._register.get_size(a)
        # NB: we don't use signed arg to give correct 2's comp result 
        result = int(bin(result, a_size), 2)
        self.log.buffer('result is {0}'.format(result))
        self._register.set_value(a, result)
        return True

    def addImmediate(self, args, instruction_decoded, **named_args):
        """Adds a register to an immediate value and stores the
        result in a second register.

        addImmediate performs twos complement arithmetic, so
        the value stored as a result of -1 + -1 will be 0xfffffffe.

        For unsigned calculations, use addImmediateUnsigned.

        Arguments:
            Args 1 and 2 should be the numbers of registers.
            args[0]:int (register)
            args[1]:int (register)
            args[2]:int (immediate)

        State changed:
             register[a]['value'] <- register[b]['value'] + c:int

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('addImmediate called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        # This will be a signed immediate value.
        c = int(instruction_decoded[args[2]], 2, signed=True)
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a, b, c))
        for operand in [a, b]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        # Convert to binary to get the correct 2's comp value.
        b_size = self._register.get_size(b)
        bin_bvalue = bin(self._register.get_value(b), size=b_size)
        bvalue = int(bin_bvalue[2:], 2, signed=True)
        #result = int(bin(self._register.get_value(b))[2:], 2, signed=True)
        result = bvalue + c
        # Need size of a, the register to be written to, for correct sign.
        size = self._register.get_size(a)
        result = int(bin(result, size), 2)
        self.log.buffer('result is {0}'.format(result))
        self._register.set_value(a, result)
        return True


    def subRegisters(self, args, instruction_decoded, **named_args):
        """args:list -> True

        Subtracts two registers and stores the result in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (register)
            args[1]:int (register)
            args[2]:int (register)

        State changed:
            register[a]['value'] <-
                register[b]['value'] - register[c]['value']

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('subRegisters called')
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{0}, 1:{1}, 2:{2}'.format(a,b,c))
        for operand in [a, b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.get_value(b) - self._register.get_value(c)
        self._register.set_value(a, result)
        return True

    def copyRegister(self, args, instruction_decoded, **named_args):
        self.log.buffer('copyRegister called')
        if args[0] in instruction_decoded.keys():
            a = int(instruction_decoded[args[0]], 2)
        else:
            a = args[0]
        if args[1] in instruction_decoded.keys():
            b = int(instruction_decoded[args[1]], 2)
        else:
            b = args[1]
        #a = args[0]
        #b = instruction_decoded[args[1]]
        self.log.buffer('args 0:{:}, 1:{:}'.format(a, b))
        value = self._register.get_value(a)
        self._register.set_value(b, value)
        return True

    def mulRegisters(self, args, instruction_decoded, **named_args):
        """args:list -> True

        Multiplies two registers and stores the product in hi and lo
        registers.

        Args:
            Each argument should be the number of a register.
            args[0]:int (high result register)
            args[1]:int (low result register)
            args[2]:int (operand)
            args[3]:int (operand)

        Returns:
            Always returns True

        Raises:
            RegisterReferenceException
        """
        self.log.buffer('mulRegisters called')
        try:
            a = int(instruction_decoded[args[0]], 2)
        except:
            a = args[0]
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        for operand in [b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.get_value(b) * self._register.get_value(c)
        self._register.set_value(a, result)
        return True

    def divRegisters(self, args, instruction_decoded, **named_args):
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
        try:
            a = int(instruction_decoded[args[0]], 2)
        except:
            a = args[0]
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        if self._register.get_value(c) == 0:
            raise ArithmeticError
        for operand in [b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.get_value(b) / self._register.get_value(c)
        self._register.set_value(a, result)
        return True

    def remRegisters(self, args, instruction_decoded, **named_args):
        """args:list -> True

        Divides two registers and stores the remainder in a third.

        Args:
            Each argument should be the number of a register.
            args[0]:int (result)
            args[1]:int (operand)
            args[2]:int (operand)

        State changed:
            register[a]['value'] <-
                register[b]['value'] % register[c]['value']

        Returns:
            Always returns True

        Raises:
            ArithmeticError
            RegisterReferenceException
        """
        self.log.buffer('remRegisters called')
        try:
            a = int(instruction_decoded[args[0]], 2)
        except:
            a = args[0]
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        if self._register.get_value(c) == 0:
            raise ArithmeticError
        for operand in [b, c]:
            if operand not in self._register.keys():
                raise RegisterReferenceException
        result = self._register.get_value(b) % self._register.get_value(c)
        self._register.set_value(a, result)
        return True

    def setRegister(self, args, instruction_decoded, **named_args):
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
        if args[0] in instruction_decoded.keys():
            a = int(instruction_decoded[args[0]], 2)
        else:
            a = args[0]
        if args[1] in instruction_decoded.keys():
            b = int(instruction_decoded[args[1]], 2)
        else:
            b = args[1]
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self._register.set_value(a, b)
        return True

    def setBitInRegister(self, args, instruction_decoded, **named_args):
        """Sets one bit in a register value to on or off.

        Description:
            (register:str, bit:int, value:int) -> return:bool

        Purpose:
            Can be used to alter registers which are commonly bit-stuffed,
            like the [E]FLAGS register of 808x ISAs.

            This call is not expected to read an instruction, so it is best
            used to generate the results of other operations, for example
            setting a carry flag as the result of an addition.

        Restrictions:
            If the register does not contain a bit_n, the result of this
            call is undefined. Registers are padded with zeros depending
            on their size specified in the ISA. This means a decimal value
            of 10 in an 0 bit register will be treated as 0b00001010.

            If the call does not contain a '0' or '1' value in the `value'
            field, the result of this call is undefined.

        Exceptions:
            This call has undefined behaviour and may not handle exceptions
            raised in the event of error.

        Returns:
            Always returns True
        """
        self.log.buffer('setBitInRegister called')
        a = args[0]
        b = int(args[1])
        c = str(args[2])
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a, b, c))

        a_size = self._register.get_size(a)

        value = list(bin(self._register.get_value(a), a_size)[2:])
        value[b] = c
        value = int(''.join(value), 2)
        self._register.set_value(a, value)

        return True

    def loadWord32(self, args, instruction_decoded, **named_args):
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
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        offset=int(c)+self._register.get_value(int(b))
        word = self._memory.get_word(offset, 32)
        self._register.set_value(int(a), word)
        self.log.buffer('loading {:} into {:} from {:}'.format(word,a,offset))
        return True

    def storeWord32(self, args, instruction_decoded, **named_args):
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
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        c = int(instruction_decoded[args[2]], 2)
        self.log.buffer('args 0:{:}, 1:{:}, 2:{:}'.format(a,b,c))
        value=self._register.get_value(int(a))
        offset=int(c)+self._register.get_value(int(b))
        self._memory.set_word(offset, value, 32)
        self.log.buffer('storing {:} in {:}'.format(value, hex(offset)))
        return True

    def testEqual(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a and b are equal.
        """
        self.log.buffer('testEqual called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        #a = int(instruction_decoded[args[0]], 2)
        #b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('a is {0}, b is {1}'.format(
            self._register.get_value(a), self._register.get_value(b)))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) == self._register.get_value(b)))
        return self._register.get_value(a) == self._register.get_value(b)

    def testNotEqual(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns false if a and b are equal.
        """
        self.log.buffer('testNotEqual called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        #a = int(instruction_decoded[args[0]], 2)
        #b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('a is {0}, b is {1}'.format(
            self._register.get_value(a), self._register.get_value(b)))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) != self._register.get_value(b)))
        return self._register.get_value(a) != self._register.get_value(b)

    def testEqualImmediate(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a and b are equal.
        """
        self.log.buffer('testEqual called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a, b))
        self.log.buffer('a is {0}, b is {1}'.format(
            self._register.get_value(a), b))
        self.log.buffer('returning {0}'.format(
            self._register.get_value(a) == b))
        return self._register.get_value(a) == b

    def testNotEqualImmediate(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns false if a and b are equal.
        """
        self.log.buffer('testNotEqual called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('a is {0}, b is {1}'.format(
            self._register.get_value(a), b))
        self.log.buffer('returning {0}'.format(
            self._register.get_value(a) != b))
        return self._register.get_value(a) != b

    def testLess(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a is less than b.
        """
        self.log.buffer('testLess called')
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) < self._register.get_value(b)))
        return self._register.get_value(a) < self._register.get_value(b)

    def testLessImmediate(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a is less than b.
        """
        self.log.buffer('testLessImmediate called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        #a = int(instruction_decoded[args[0]], 2)
        #b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) < b))
        return self._register.get_value(a) < b

    def testGreater(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a > b.
        """
        self.log.buffer('testGreater called')
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'
                        .format(self._register.get_value(a) > self._register.get_value(b)))
        return self._register.get_value(a) > self._register.get_value(b)

    def testGreaterOrEqual(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a >= b.
        """
        self.log.buffer('testGreaterOrEqual called')
        a = int(instruction_decoded[args[0]], 2)
        b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) >= self._register.get_value(b)))
        return self._register.get_value(a) >= self._register.get_value(b)

    def testGreaterImmediate(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Returns true if a > b.
        """
        self.log.buffer('testGreaterImmediate called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        #a = int(instruction_decoded[args[0]], 2)
        #b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) > b))
        return self._register.get_value(a) > b

    def testGreaterOrEqualImmediate(self, args, instruction_decoded, **named_args):
        """args:list -> bool

        Values:
            a = Register
            b = Register

        Returns true if a >= b.
        """
        self.log.buffer('testGreaterOrEqualImmediate called')
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = self._decode_register_reference(args[1], instruction_decoded)
        #a = int(instruction_decoded[args[0]], 2)
        #b = int(instruction_decoded[args[1]], 2)
        self.log.buffer('args 0:{0}, 1:{1}'.format(a,b))
        self.log.buffer('returning {0}'.format(self._register.get_value(a) >= b))
        return self._register.get_value(a) >= b

    # TODO: Add log items to test..[On|Off]. (2011-08-19)
    def testBitIsOn(self, args, instruction_decoded, **named_args):
        """Returns true if register has bit_n set to 0b1

        Description:
            (register:str, int:int) -> return:bool
            testBitIsOn inspects one bit of a binary value stored in
            a register and returns True or False. This call behaves
            as if the storage were big-endian, regardless of the underlying
            ISA and other organization.


        Purpose:
            Can be used to examine registers which are commonly bit-stuffed,
            like the [E]FLAGS register of 808x ISAs.

        Restrictions:
            If the register does not contain a bit_n, the result of this
            call is undefined. Registers are padded with zeros depending
            on their size specified in the ISA. This means a value of 0b1
            in an 0 bit register will be examined as 0b00000001, so bit
            0..6 will appear to be off and 7 will appear on.

        Exceptions:
            This call has undefined behaviour and may not handle exceptions
            raised in the event of error.

        Returns:
            True or False
        """
        a = args[0]
        b = args[1]

        size  = self._register.get_size(a)
        value = list(bin(self._register.get_value(a), size)[2:])

        return value[b] == '1'

    def testBitIsOff(self, args, instruction_decoded, **named_args):
        """Returns true if register has bit_n set to 0b0

        Description:
            (register:str, int:int) -> return:bool
            testBitIsOff inspects one bit of a binary value stored in
            a register and returns True or False. This call behaves
            as if the storage were big-endian, regardless of the underlying
            ISA and other organization.


        Purpose:
            Can be used to examine registers which are commonly bit-stuffed,
            like the [E]FLAGS register of 808x ISAs.

        Restrictions:
            If the register does not contain a bit_n, the result of this
            call is undefined. Registers are padded with zeros depending
            on their size specified in the ISA. This means a value of 0b1
            in an 0 bit register will be examined as 0b00000001, so bit
            0..6 will appear to be off and 7 will appear on.

        Exceptions:
            This call has undefined behaviour and may not handle exceptions
            raised in the event of error.

        Returns:
            True or False
        """
        a = self._decode_register_reference(args[0], instruction_decoded)
        b = args[1]

        size  = self._register.get_size(a)
        value = list(bin(self._register.get_value(a), size)[2:])

        return value[b] == '0'

    def branchAbsolute(self, args, instruction_decoded, **named_args):
        """Sets the instruction pointer to a new memory address.

        Values:
            a = int
           [b = int]

           Takes an optional second argument which can be used
           to simulate a jump return offset amongst other things.

        Returns True
        """
        self.log.buffer('branchAbsolute called')
        a = int(instruction_decoded[args[0]], 2)
        self.log.buffer('args 0:{:}'.format(a)),
        # add branch delay
        if len(args) > 1:
            b = int(self._register.get_value(args[1]))
            self.log.buffer('args 1:{:}'.format(b))
            word_space = self._memory.get_word_spacing()
            b = b * word_space
            a = a + b
        pc=self._register.get_pc()
        self._register.set_value(pc, a)
        return True

    def branchRelative(self, args, instruction_decoded, **named_args):
        """Adds a computed offset to the instruction pointer.

        Values:
            a = int

        Returns True
        """
        self.log.buffer('branchRelative called')
        a = int(instruction_decoded[args[0]], 2, signed=True)
        self.log.buffer('args 0:{0}'.format(a))
        # add branch delay
        if len(args) > 1:
            b=args[1]
            a = a + b
        pc = self._register.get_pc()
        pc_value = self._register.get_value(pc)
        self.log.buffer('pc is {:}'.format(hex(pc_value)))
        word_space = self._memory.get_word_spacing()
        self.log.buffer('word-space is {:}'.format(word_space))
        index = named_args['branch_offset']
        a = a - index
        a = a * word_space
        self.log.buffer('increment is {:}'.format(a))
        a = pc_value + a
        self._register.set_value(pc, a)
        return True

    def incrementPc(self, args, instruction_decoded, **named_args):
        """args:list -> True"""
        self.log.buffer('incrementPc called')
        a = int(instruction_decoded[args[0]], 2)
        pc=self._register.get_pc()
        value=self._register.get_value(pc)+a
        self._register.set_value(pc, value)
        return True

    def doNothing(self, args, instruction_decoded, **named_args):
        """args:list -> True"""
        self.log.buffer('doNothing called')
        return True

    def systemCall(self, args, instruction_decoded, **named_args):
        """args:list -> True"""
        self.log.buffer('systemCall called')
        system_call = SystemCall()
        try:
            if args[0][:3] == 'DIR':
                a = int(args[0][3:], 16)
                result = a
        except:
            a = args[0]
            result = self._register.get_value(a)
        self.log.buffer('args 0:{0}'.format(a))
        system_call.service(result)
        return True
