#!/usr/bin/env python
#
# Cli Client.
# file           : cli.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-15
# last modified  : 2011-08-04


import sys
import traceback
try:
    import readline
except:
    pass # never mind, too system specific

from core import *
from copy import deepcopy

from module.Interface   import UpdateListener
from module.Evaluator   import Evaluator
from module.Parser      import Parser
from module.Memory      import AlignmentError
from module.Interpreter import BadInstructionOrSyntax
from module.Interpreter import DataMissingException
from module.Interpreter import DataConversionFromUnknownType
from module.SystemCall  import SigTerm

# TODO: Replace __all__ imports with named. (2011-08-03)
from module.lib.Header    import *
from module.lib.Functions import binary as bin
from module.lib.Functions import hexadecimal as hex

class Cli(UpdateListener):
    """``Cli is just this guy, you know?''
                                    --Gag Halfrunt
    """
    def __init__(self, config):

        # DEBUG Levels:
        # 1: minimal feedback, short traceback and frame data
        # 2: normal feedback, full traceback
        # ...
        # 11: reserved for _really_ annoying messages that are
        #     rarely useful.
        self.local_DEBUG = 2

        self.simulation  = None
        self.last_cmd    = None
        self.registers   = []
        self.memory      = []
        self.pipeline    = []

        try:
        # We can try to use a history file, but readline may not
        # be present on the host system.
            readline.read_history_file('.cli_history')
        except:
            pass

        try:
            self.simulation=Simulation(config=config,
                                       logfile='logs/cli.log')

        # Avoid some unnecessary crashes:
        # Authorization from the system ensures necessary methods
        # are implemented in the client. This is NOT done by base
        # class checking, so client is not required to be a subclass.
            self.simulation.connect(self)
        # FIX: Legacy? 2011-08-04
            self.size = self.simulation.get_instruction_size()
        except Exception, e:
            self.exception_handler(e)

        try:
            self.run()
        except KeyboardInterrupt, e:
            print('^C')
            self.exit()
        except EOFError, e:
            print('^D')
            self.exit()
        except Exception, e:
            self.exception_handler(e)

#
# Loop
#

    def run(self):
        print("Command Line Client (r{:}:{:})\n"
              .format(VERSION, RELEASE_NAME) +
              "Type `help', `license' or `version' for more information.")
        parser = Parser()
        while True:
            try:
                line = raw_input(">>> ")
                if len(line) > 0:
                    self.last_command = line
                elif len(self.last_command) > 0:
                    line = self.last_command
                (function, args) = parser.parse(line)
                # Special debug level, 11, because this warning is simply
                # f..king anoying.
                if self.local_DEBUG >= 11:
                    print("DEBUG {:}".format(args))
                try:
                    call = getattr(self, function)
                    if args:
                        call(args)
                    else:
                        call()
                except Exception, e:
                    raise e
            except SigTerm:
                print('Programme finished')

#
# Basic Control
#

    def load(self, filename=False):
        if filename:
            try:
                self.reset()
                text = self.simulation.load(filename, self)
                self._programme_text = text
                print("Loaded {:} word programme, `{:}'"
                      .format(len(text[0]), ''.join(filename.split('/')[-1:])))
            except IOError, e:
                sys.stderr.write("No such file: `{:}'\n".format(filename))
            except BadInstructionOrSyntax, e:
                print('File contains errors:\n{:}'.format(e.message))
            except Exception, e:
                self.exception_handler(e)
        else:
            print("Please supply a filename to read")

    def reset(self):
        if hasattr(self, "_programme_text"):
            del self._programme_text
        self.simulation.reset(self)

    def exit(self, *args, **kwargs):
        """Exit the simulation cleanly."""
        if len(args) < 1:
            args=[0]
            print("Exit")
        readline.write_history_file('.cli_history')
        if callable(self.simulation):
            self.simulation.disconnect(self)
        sys.exit(args[0])

#
# Update Functions
#

    def step(self):
        """Execute one instruction."""
        self.simulation.step(self)

    def cycle(self):
        """Process one CPU cycle."""
        self.simulation.cycle(self)

    def complete(self):
        """Go Forever."""
        self.simulation.run(self)

    def update(self, *args, **kwargs):
        """Callback for Broadcaster object."""
        for memento in [self.registers, self.memory, self.pipeline]:
            if len(memento) > 10:
                memento.pop(0)
        self.registers.append(kwargs['registers'])
        self.memory.append(kwargs['memory'])
        self.pipeline.append(kwargs['pipeline'])

#
# Modules Providing Functions
#

    def evaluate(self):
        try:
            evaluator = Evaluator(simulation=self.simulation, client=self)
            evaluator.eval()
        except BadInstructionOrSyntax, e:
            print(e.message)
        except Exception, e:
            print('fatal: {:}'.format(e))

    def visualize(self, args=None):
        from module.Visualizer  import Visualizer
        # Instance of visualizer if there ain't one
        if args == "kill":
            if hasattr(self, 'visualizer'):
                self.visualizer.__del__()
                del self.visualizer
            return
        if not hasattr(self, 'visualizer'):
            self.visualizer = Visualizer(
                self.simulation.get_monitor())
        # Initialize if not yet done. These are once only actions.
        if not self.visualizer.is_initialized():
            self.visualizer.add_representation_from_data(
                "processor_cycles", opacity=1.0, colour='magenta')
        # Need a boradcast source, at least for update notifications
        # (UpdateListener).
            self.visualizer.add_broadcast_data_source(
                self.simulation.get_processor())
        # We will link-render, which sets the window to redraw when
        # there is a change in the broadcaster (Processor).
            window_title = "CLI::Visualizer (r{:}:{:})".format(
                VERSION, RELEASE_NAME)
            self.visualizer.initialize(
                name=window_title, link_render=True)
        # One off render to display the window.
        self.visualizer.render()

#
# Print Functions
#

    def print_programme(self):
        if hasattr(self, "_programme_text"):
            print("{:-<80}".format("--Programme"))
            for i in range(len(self._programme_text[0])):
                print("{:<12}{:<24}{:}".format(hex(self._programme_text[2][i]),
                                        self._programme_text[0][i],
                                        bin(self._programme_text[1][i],
                                           self.size)[2:]
                                       ))
            print("{:-<80}".format(''))
        else:
            print('No programme loaded')

    def print_registers(self, args=None):
        """Formats and outputs a display of the registers"""
        # We can do rewinds, which pulls a previous register state off
        # the stack and displays that. Frames are minus indexed from the
        # top of the stack, possibly because of idiocy, possibly it was
        # a good decision at the time.
        if type(args) == dict and args.has_key('rewind'):
            frame = -(int(args['rewind'])+1)
            args.clear()
        else:
        # The default frame is -1, the top of the stack.
            frame = -1
        try:
        # grab the correct frame if rewind is requested
            r=self.registers[frame]
        except IndexError:
            print("Can't rewind {:}, only {:} values stored."
                  .format(abs(frame)-1, len(self.registers)))
            return
        try:
            if self.local_DEBUG > 0:
            # Print frame information for debugging.
            # Include object id and clean up the hex string.
                print("{:-<80}".format("--Registers DEBUG-Frame-{:}"
                                       .format(hex(id(r))[2:].replace('L', ''))))
            else:
                print("{:-<80}".format("--Registers"))
            for i in r.values():
                if i>0 and i % 4 == 0:
                    print('')
                # Get the name of the register.
                name = self.registers[frame].get_number_name_mappings()[i]
                # Print name, number and hex value.
                print("{:>4}({:0>2}):{:.>10}"
                      .format(name[:4], i,
                      hex(r.get_value(i))[2:].replace('L', ''), 8)),
            print("\n{:-<80}".format(''))
        except Exception, e:
            print("An error occurred fetching data from registers:\n{:}"
                  .format(e.message))

    def print_register(self, args):
        """Formats and outputs display of a single register"""
        base   = 'd'
        number = 0
        args = args.split()
        if not args[0].isdigit():
            number = int(args[0][:-1])
            value  = self.registers[-1].get_value(number)
            base   = args[0][-1:]
        else:
            number = int(args[0])
            value = self.registers[-1].get_value(number)
        name = self.registers[-1].get_number_name_mappings()[number]
        print("{:}({:}):".format(name, number)),
        if len(args) > 1:
            base = args[1]
        if base =='d':
            print("{:}".format(value))
        elif base =='x' or base == 'h':
            print("{:}".format(hex(value)[2:].replace('L', '')))
        elif base =='b':
            print("{:}".format(bin(value, self.size)[2:]))
        else:
        # Frowny is the closest we're getting to an easter egg.
            print(":-(\n{:} is not a number format (d:dec, [h,x]:hex, b:bin)"
                 .format(base))

    def print_pipeline(self):
        """Formats and outputs a display of the pipeline"""
        #the if block is just a hack to make exceptions more consistent
        #print(self._programme_text)
        # FIX: Pipeline is not updated on last cycle. (2011-08-04)
        print("{:-<80}".format('--Pipeline'))
        if len(self.pipeline[-1]) == 0:
            print(" Begin simulation to see the pipeline")
        else:
            for i in range(len(self.pipeline[-1])):
                if i > len(self._programme_text[1]):
                # Probably some error with the programme, maybe
                # not serious. Return to avoid crashing.
                    return
                index = self._programme_text[1].index(self.pipeline[-1][i])
                print("Stage {:}:{:}  {:}"
                     .format(i+1,
                             bin(int(self.pipeline[-1][i]), self.size)[2:],
                             self._programme_text[0][index]
                            ))
        print("{:-<80}".format(''))

    def print_memory(self, **kwargs):
        """Format and print a view of the memory."""
        # TODO: Select which memory slice to print. (2011-08-05)
        try:
            end=int(kwargs['end'])
            print(int(kwargs['end']))
        except:
            end=None
        memory_slice = self.memory[-1].get_slice(end=end).items()
        print("{:-<80}".format('--Memory'))
        for address, value in sorted(memory_slice, reverse=True):
            print(" 0x{:0>8}: {:}  0x{:0>8}"
                 .format(hex(address)[2:], bin(value,self.size)[2:],
                         hex(value)[2:]))
        print("{:-<80}".format(''))

    def print_visualization_modules(self):
        print '\n'.join(
            self.simulation.get_monitor().list_int_props())

#
# Documentation Functions
#

    def usage(self, args):
        usage   = {'print':'print <reg[ister[s]]>|<prog[ramme]>'}
        command = ''
        if args.has_key('fun'):
            command = args['fun']
        if usage.has_key(command):
            print('Usage: ' + usage[command])
        else:
            print("Bad command: `{:}'. Try `help'".format(command))

    def help(self):
        print('help will go here')

    def license(self):
        print(LICENSE)

    def version(self):
        print(VERSION)

#
# Helper Functions
#
    def exception_handler(self, e):
        if DEBUG and self.local_DEBUG < 1:
            print("Unhandled exception: {:}".format(e))
        elif DEBUG and self.local_DEBUG >= 1:
            traceback.print_exc(file=sys.stderr)
        elif DEBUG and self.local_DEBUG >= 2:
            print('Type: ' + e.__class__.__name__)
        self.exit(1)




if __name__ == '__main__':
    if len(sys.argv) > 1:
        Cli(sys.argv[1])
    else:
        sys.stderr.write('Usage: cli <config package>\n')
