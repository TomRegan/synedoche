#!/usr/bin/env python
#
# Command Line Parser.
# file           : Parser.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-28
# last modified  : 2011-07-28

class BaseParser(object):
    def parse(self, line):
        pass

class Parser(BaseParser):
    def parse(self, line):
        """line:str -> ...

        Reads a line of input, executing any commands recognized.

        Raises:
            Exception.
            Exceptions from other frames must be handled.
        """
        line=line.split()
        if line[0][:2] == 'pr':
            if len(line) > 1:
                if line[1][:3] == 'reg':
                    if len(line) > 2:
                        return ('print_register', line[2:])
                        #self.print_register(*line[2:])
                    else:
                        return ('print_registers')
                        #self.print_registers()
                elif line[1][:3] == 'pip':
                    return ('print_pipeline')
                    #self.print_pipeline()
                elif line[1][:3] == 'mem':
                    if len(line) > 2:
                        return ('print_memory', line[2])
                        #self.print_memory(end=line[2])
                    else:
                        return ('print_memory')
                        #self.print_memory()
                elif line[1][:3] == "pro":
                    return ('print_programme')
                    #self.print_programme()
                else:
                    print("Not a print function: `{:}'"
                          .format(line[1]))
            else:
                return ('usage')
                #self.usage(fun='print')
        elif line[0] == 'help':
            return ('help')
            #self.help()
        elif line[0][:4] == 'vers':
            return ('version')
            #print(VERSION)
        elif line[0][:4] == 'lice':
            return ('license')
            #print(LICENSE)
        elif line[0][:4] == 'rese':
            if line[0] != 'reset':
                print(':reset')
            return ('reset')
            #self.reset()
        elif line[0][:1] == 's':
            if line[0] != 'step':
                print(':step')
            return ('step')
            #self.step()
        elif line[0][:1] == 'c':
            if line[0] != 'cycle':
                print(':cycle')
            return ('step')
            self.cycle()
        elif line[0][:1] == 'l':
            if line[0] != 'load':
                print(':load')
            if len(line) > 1:
                return ('load', line[1])
                self.load(line[1])
            else: print "Please supply a filename to read"
        elif line[0][:4] == 'eval':
            try:
                evaluator = Evaluator(simulation=self.simulation,
                                      client=self)
                evaluator.eval()
            except BadInstructionOrSyntax, e:
                print(e.message)
            except Exception, e:
                print('fatal: {:}'.format(e))
        elif line[0] == '__except__':
            raise Exception('Intentionally raised exception in {:}'
                            .format(self.__class__.__name__))
        elif line[0] == 'quit'\
            or line[0] == 'exit'\
            or line[0] == '\e':
            return ('exit')
            #self.exit()
        else:
            return ('usage', {'fun':' '.join(line)})
            #self.usage(fun=' '.join(line))
