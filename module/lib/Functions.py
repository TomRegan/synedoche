#!/usr/bin/env python
#
# Helper Functions.
# file           : Functions.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-19
# last modified  : 2011-08-04

#!/usr/bin/env python

def binary(number, size=1, extend=False):
    """Improved bin function that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    if extend:
        extension = size - len(bin(number))
        character = bin(number)[2:][0]
        return "0b" + (character * extension) + bin(number)[2:]
    else:
        return '0b' + bin(number)[2:].zfill(size)

def integer(number, *args, **kwargs):
    """Improved int function that can return the correct value of a
    binary number in twos compliment
    """
    if len(kwargs) > 0 and kwargs['signed'] and number[0] == '1':
        return -(-(int(number, *args))+(2**len(number)))
    return int(number, *args)

def hexadecimal(number, size=1):
    """Improved hex function that can return two's complement numbers"""
    if number < 0:
        number = 2**size + number
    return '0x' + hex(number)[2:].zfill(size).replace('L', '')

def dump_accessors(reference):
    """Function to print out a list of all the accessors belonging to
    an object (a bit crude, but has proved helpful for debugging).
    """
    for data in dir(reference):
        if data[:3] == 'get':
            call=getattr(reference, data)
            print "{0}\n{1}\n".format(data,call())

def asciify(string):
    """Returns a string encoded as ascii"""
    return string.encode('ascii')

def size(obj):
    """Returns the size of an object in bytes"""
    try:
        return obj.__sizeof__()
    except:
        return 0

def clear_print(string):
    """Clears a line and prints a string."""
    print(chr(27) + '[A'+' '*80)
    print(chr(27) + '[A' + string)

