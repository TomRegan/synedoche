#!/usr/bin/env python

def binary(number, size=1, extend=False):
    """Improved bin funciton that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    if extend:
        extension = size - len(bin(number))
        character = bin(number)[2:][0]
        return "0b" + (character * extension) + bin(number)[2:]
    else:
        return '0b' + bin(number)[2:].zfill(size)

def integer(number, *args, **kwargs):
    if len(kwargs) > 0 and kwargs['signed'] and number[0] == '1':
        return -(-(int(number, *args))+(2**len(number)))
    return int(number, *args)

def hexadecimal(number, size=1):
    """Improved hex funciton that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    return '0x' + hex(number)[2:].zfill(size)

def dump_accessors(reference):
    for data in dir(reference):
        if data[:3] == 'get':
            call=getattr(reference,data)
            print "{0}\n{1}\n".format(data,call())

def asciify(string):
    """Returns a string encoded as ascii"""
    return string.encode('ascii')

def size(thing):
    """Returns the size of an object in bytes"""
    try:
        return thing.__sizeof__()
    except:
        return 0
