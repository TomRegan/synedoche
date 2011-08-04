#!/usr/bin/env python
#
# String Parser.
# file           : Parser.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-28
# last modified  : 2011-08-04

class BaseParser(object):
    def parse(self, line):
        pass

class Parser(BaseParser):
    def parse(self, line):
        """Reads a line of input and returns a tuple:
            (method:str, args:tuple)

        Raises:
            Exception.
            NB: Exceptions from other frames must be handled.
        """
        tokens  = line.split()
        command = tokens.pop(0)
        if command[:2] == 'pr':
            return self._print(tokens)
        elif command == 'help':
            return ('help', ())
        elif command == 'usage':
            return ('usage', {'fun':tokens[0]})
        elif command[:4] == 'vers':
            return ('version', ())
        elif command[:4] == 'lice':
            return ('license', ())
        elif command[:4] == 'rese':
            if command != 'reset':
                print(':reset')
            return ('reset', ())
        elif command[:1] == 's':
            if command != 'step':
                print(':step')
            return ('step', ())
        elif command[:1] == 'c':
            if command != 'cycle':
                print(':cycle')
            return ('cycle', ())
        elif command[:1] == 'l':
            if command != 'load':
                print(':load')
            return self._load(tokens)
        elif command[:4] == 'eval':
            if command != 'evaluate':
                print("evaluate")
            return ('evaluate', ())
        elif command == '__except__':
            raise Exception('Intentionally raised exception in {:} object'
                            .format(self.__class__.__name__.lower()))
        elif command == 'quit'\
            or command == 'exit'\
            or command == '\e':
            return ('exit')
        else:
            return ('usage', {'fun': command})
            #self.usage(fun=' '.join(line))

    def _print(self, tokens):
        if len(tokens) > 0:
            if tokens[0][:3] == 'reg':
                if len(tokens) > 1:
                    if tokens[1][:2] == 're' and len(tokens) > 2:
                        return ('print_registers', {'rewind':tokens[2]})
                    else:
                        return ('print_register', (tokens[1]))
                else:
                    return ('print_registers', ())
            elif tokens[0][:3] == 'pip':
                return ('print_pipeline', ())
            elif tokens[0][:3] == 'mem':
                return ('print_memory', ())
            elif tokens[0][:3] == "pro":
                return ('print_programme', ())
            else:
                pass
        else:
            return ('usage', {'fun':'print'})

    def _load(self, tokens):
        if len(tokens) > 0:
            return ('load', tokens[0])
        else:
            return ('load', False)
