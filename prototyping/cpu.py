#!/usr/bin/env python

''' cpu.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-06-23
description: prototype for the cpu functions
'''

"""IMPORTANT
need to decide if I will encapsulate cpu data here, therefore
requiring register subscript to be specified, or to allow a
foreign cpu object to pass its registers as args (preferred)

This may pave the way to SMP.
"""

class Cpu(object):
  """Data for a CPU object"""
  registers=[0,1,2,3,4,5]
  memory={}

def CpuAddRegisters(a,b,c):
  """Updates register a with the sum of b and c"""
  try:
    Cpu.registers[a]=Cpu.registers[b] + Cpu.registers[c]
  except Exception, e:
    pass #noexcept
  finally:
    pass #nofinally

def CpuSubRegisters(a,b,c):
  """Updates register a with the difference between b and c"""
  try:
    Cpu.registers[a]=Cpu.registers[b] - Cpu.registers[c]
  except Exception, e:
    pass #noexcept
  finally:
    pass #nofinally

def CpuMulRegisters(a,b,c):
  """Updates register a with the product of b and c"""
  try:
    Cpu.registers[a]=Cpu.registers[b] * Cpu.registers[c]
  except Exception, e:
    pass #noexcept
  finally:
    pass #nofinally

def CpuDivRegisters(a,b,c):
  """Updates register a with the dividend of b and c"""
  try:
    Cpu.registers[a]=b/c
  except Exception, e:
    pass #noexcept
  finally:
    pass #nofinally

def CpuSetRegister(a,b):
  """Updates register a with the value b"""
  try:
    Cpu.registers[a]=b
  except Exception, e:
    pass #noexcept
  finally:
    pass #nofinally

def CpuLoadWord32(a,b):
  """Loads the word at b into register a"""
  """we need to do some bounds checking in a later iteration!"""
  Cpu.registers[a]=Cpu.memory[b]

def CpuStoreWord32(a,b):
  """Stores the contents of register a at memory location b"""
  """we need to do some bounds checking in a later iteration!"""
  Cpu.memory[b]=Cpu.registers[a]

def CpuTestEqual(a,b):
  """Returns true if a and b are equal"""
  return a==b

def CpuTestNotEqual(a,b):
  """Returns false if a and b are equal"""
  return a != b

def CpuTestLess(a,b):
  """Returns true if a is less than b"""
  return a < b

def CpuTestGreater(a,b):
  """Returns true if a is greater than b"""
  return a > b
