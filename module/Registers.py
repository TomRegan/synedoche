#!/usr/bin/env python
#coding=iso-8859-15
#
# Register Component.
# file           : Registers.py
# author         : Tom Regan <noreply.tom.regan@gmail.com>
# since          : 2011-07-11
# last modified  : 2011-08-10

from copy import deepcopy
from Logger    import RegisterLogger
from Logger    import level
from Interface import LoggerClient
from lib.Functions import hexadecimal as hex

class BaseRegisters(LoggerClient, ):
    def open_log(self, logger):
        self.log = RegisterLogger(logger)
        self.log.buffer("created registers, `{:}'"
                        .format(self.__class__.__name__), level.INFO)

    def open_monitor(self, monitor):
        self.log.write("Attempted to attach monitor", level.ERROR)

class Registers(BaseRegisters):
    """Provides an interface that should be used to build a set of registers

    Usage:
        registers=Registers()
        registers.addRegister(number=0, value=2147483647, size=32,
                              profile='gp', privilege=True)
        registers.remove_register(0)
    """

    _registers    = {}
    _registers_iv = {}
    _name_number  = {}
    _number_name  = {}

    def __init__(self, log=None):
        if log != None:
            self.open_log(log)

    def __copy__(self):
        #
        # Overriding copy instead of deepcopy because it's simpler.
        # Beaucoup problems in UTs reading data from _registers
        # although problem wasn't obvious in use with cli client.
        #
        new = Registers()
        new._registers = deepcopy(self._registers)
        return new

    def add_register(self, number, value, size, profile, privilege):
        """(number:int, value:int, size:int, profile:str, privilege:bool)
            -> registers{register[number]:{value,size,profile,provilege}:dict

        Adds a register.
        """

        self._registers[number] = {}
        self._registers[number]['value']     = value
        self._registers[number]['size']      = size
        self._registers[number]['profile']   = profile
        self._registers[number]['privilege'] = privilege
        self.log.buffer('added register: {:>2} {:>12} {:} {:>3} {:}'
                        .format(number, value, size, profile, privilege),
                        level.FINEST)
        self._registers_iv = deepcopy(self._registers)

    def add_register_mapping(self, name, number):
        """(name:str, number:int) -> register{name:number}:dict

        Creates a map of names to registers which can be used to
        assist decoding assembly instructions.
        """

        self._name_number[name]   = number
        self._number_name[number] = name

    def remove_register(self, number):
        """Deletes a register."""
        del self._registers[number]

    def set_value(self, number, value):
        """number:int -> ...
        Stores a value in a register.
        """
        if number not in self.keys():
            return
        name = self._number_name[number]
        self.log.buffer("setting {:} to {:}".format(name, hex(value, 8)),
                        level.FINER)
        self._registers[number]['value']=value

    def get_value(self, number):
        """Returns the value stored in a register."""
        if number not in self.keys():
            # TODO: Raise register reference exception? (2011-08-05)
            return
        return self._registers[number]['value']

    def get_size(self, number):
        """Returns the width of a register in bits."""
        if number not in self.keys():
            return 0
        return self._registers[number]['size']

    def increment(self, number, amount=1):
        """(number:int, amount=1:int) -> ...
        Increases the value in a register
        """
        name = self._number_name[number]
        self.log.buffer("adding {:} to {:}".format(amount, name),
                        level.FINEST)
        value = self._registers[number]['value']+amount
        self.set_value(number, value)

    def get_pc(self):
        """-> register:int
        Returns the number of the register with the program counter.
        """
        return map(lambda x: x['profile'] == 'pc',
                 self._registers.values()).index(True)

    def reset(self):
        """Resets all registers to beginning values"""
        self.log.buffer("clearing register values", level.FINER)
        self._registers = deepcopy(self._registers_iv)

    def keys(self):
        return self._registers.keys()

    def values(self):
        values={}
        for register in self._registers:
            values[register]=self._registers[register]['value']
        return values

    def get_registers(self):
        """... -> registers:object

        Returns a reference to register object.
        """
        # Do _not_ .... with this. Making it deepcopy breaks lots.
        return self

    def get_register_mappings(self):
        """... -> registers{name:str->number:int}:dict

        Returns a dict of register mappings.
        """
        return self._name_number

    def get_number_name_mappings(self):
        """--- -> registers{number:int->name:str}:dict
        Returns a dict of register mappings.
        """
        return self._number_name

    def get_utilization(self):
        """Returns a ratio of registers used 0 ≤ n ≤ 1.0."""
        changed = 0
        for n in self._registers:
            if self._registers[n]['value'] != self._registers_iv[n]['value']:
                changed = changed + 1
        return changed
