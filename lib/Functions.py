#!/usr/bin/env python

def binary(number, size=1):
    """Improved bin funciton that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    return '0b' + bin(number)[2:].zfill(size)

def hexadecimal(number, size=1):
    """Improved hex funciton that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    return '0x' + hex(number)[2:].zfill(size)

def dumpAccessors(reference):
    for data in dir(reference):
        if data[:3] == 'get':
            call=getattr(reference,data)
            print "{0}\n{1}\n".format(data,call())

def asciify(string):
    """Returns a string encoded as ascii"""
    return string.encode('ascii')
