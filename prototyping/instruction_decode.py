#!/usr/bin/env python

""" instruction_decode.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-06-21
description: prototype code that identifies instructions
"""

import sys

def main():
  """prototype for instruction decoding and identification"""

  instructionRaw='00000000000000000000000000100000' #test instruction

  opcodeLength=6
  operationName='not_found'

  instructionType=''
  instructionDecoded={}

  instructionTypes={}
  instructionTypes['r']={'op':(0,5),'fn':(26,31)}
  instructionTypes['i']={'op':(0,5),'fn':(26,31)}
  instructionTypes['j']={'op':(0,5),'fn':( 6,31)}

  signatures={}
  signatures['add']={'op':'000000','fn':'100000'}
  signatures['sub']={'op':'000000','fn':'101000'}


  if instructionRaw[:opcodeLength] == '000000':
    instructionType='r'
  for field in instructionTypes[instructionType]:
    """reencode the instruction as a hash of fields"""
    a=instructionTypes[instructionType][field][0] #a<-start of field
    b=instructionTypes[instructionType][field][1] #b<-end of field
    instructionDecoded[field]=instructionRaw[a:b+1]
  print 'Instruction %s' % instructionDecoded

  #temporaryInstruction={}
  #for signature in signatures:
  #  """identify the instruction by its signature"""
  #  for field in signatures[signature]:
  #    if field in instructionDecoded:
  #      temporaryInstruction[field]=instructionDecoded[field]
  #  if temporaryInstruction == signatures[signature]:
  #    operationName=signature
  p=set(instructionDecoded.items())
  for signature in signatures:
    """identify the instruction by its signature"""
    q=set(signatures[signature].items())
    if p & q == set(signatures[signature].items()):
      operationName=signature

  print 'Operation: %s' % operationName


if __name__ == '__main__':
  sys.stderr.write("Do not run this script as main. Write a unit test!\n")
  main()

"""
@license
Copyright (C) 2011 Tom Regan <thomas.c.regan@gmail.com>.
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
