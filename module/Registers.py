#!/usr/bin/env python
''' Registers.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-11
description: A Rewrite of System.Registers
'''

class Registers(object):
    """Provides an interface that should be used to build a set of registers

    Usage:
        registers=Registers()
        registers.addRegister(number=0, value=2147483647, size=32,
                              profile='gp', privilege=True)
        registers.removeRegister(0)
    """

    _registers={}
    _register_mappings={}
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

    def addRegisterMapping(self, name, number):
        """(name:str, number:int) -> register{name:number}:dict

        Creates a map of names to registers which can be used to
        assist decoding assembly instructions.
        """

        self._register_mappings[name]=number

    def removeRegister(self, number):
        """number:int -> ...

        Deletes a register.
        """

        del self._registers[number]

    def getRegisters(self):
        """... -> registers:object

        Returns a reference to register object.
        """

        return self._registers

    def getRegisterMappings(self):
        """... -> registers{name:number}:dict

        Returns a dict of register mappings.
        """
        return self._register_mappings
