#!/usr/bin/env python
#
# Cli Client.
# file           : cli.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-15
# last modified  : 2011-08-12


import sys
import traceback
try:
    import readline
except: pass

from core import Simulation

from module.Interface   import UpdateListener
from module.Evaluator   import Evaluator
from module.Parser      import Parser
from module.Completer   import Completer
from module.Memory      import AlignmentError, AddressingError
from module.Assembler   import BadInstructionOrSyntax
from module.Memory      import SegmentationFaultException
from module.System      import SigTerm, SigTrap, SigFpe, SigXCpu, SigIll

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
        self.local_DEBUG = 0

        self.simulation  = None
        self.last_cmd    = None
        self.registers   = []
        self.memory      = []
        self.pipeline    = []
        self.updated     = False

        try:
        # We can try to use a history file, but readline may not
        # be present on the host system.
            readline.read_history_file('.cli_history')
        except: pass

        try:
            self.simulation = Simulation(config = config,
                                         logfile='logs/cli.log')

        # Avoid some unnecessary crashes:
        # Authorization from the system ensures necessary methods
        # are implemented in the client. This is NOT done by base
        # class checking, so client is not required to be a subclass.
            self.simulation.connect(self)
        # FIX: This seems to be broken: we're using the instruction
        # size to determine the size of the address bus. (2011-08-07)
            self.isize = self.simulation.get_isa().getSize()
            self.word_size = self.simulation.get_memory().get_word_size()
            self.byte_size = self.simulation.get_memory().get_word_spacing()
        except IOError, e:
            sys.stderr.write("Couldn't find configuration file: `{:}'\n"
                             .format(config))
            sys.exit()
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
                readline.parse_and_bind("tab: complete")
                vocabulary = ['load', 'run', 'print',
                              'register', 'memory',
                              'program', 'version',
                              'contunue',
                              'help', 'license']
                readline.set_completer_delims(
                    ' \t\n`~...@#$%^&*()-=+[{]}\\|;:\'",<>?')
                completer = Completer(vocabulary)
                readline.set_completer(completer.complete)
            except: pass
            try:
                line = raw_input(">>> ")
                if len(line) > 0:
                    self.last_command = line
                elif len(self.last_command) > 0:
                    line = self.last_command
                (function, args) = parser.parse(line)
                # Special debug level, 11, because this warning is usually
                # ....... anoying.
                if self.local_DEBUG >= 11:
                    print("DEBUG {:}".format(args))
                # FIX: Why is this exception block not in use?
                # (2011-08-12)
                #try:
                call = getattr(self, function)
                if args:
                    call(args)
                else:
                    call()
                #except Exception, e:
                #    raise e
            except AlignmentError, e:
                print("Alignment Error: {:}".format(e.message))
            except AddressingError, e:
                print("Addressing Error: {:}".format(e.message))
            except SegmentationFaultException, e:
                print('SIGSEGV ({:})'.format(e.message))
            except SigTerm:
                # FIX: Won't work on NT platform. (2011-08-30)
                print(chr(27) + '[AProgram finished')
            except SigTrap:
                print('Breaking')
            except SigFpe, e:
                print(e.message)
            except SigXCpu, e:
                print(e.message)
            except SigIll, e:
                print(e.message)

#
# Basic Control
#

    def load(self, filename=False):
        if filename:
            try:
                self.reset()
                text = self.simulation.load(filename, self)
                self._program_text = text
                print("Loaded {:} word program, `{:}'"
                      .format(len(text[0]), ''.join(filename.split('/')[-1:])))
                self._program_name = filename
            except IOError, e:
                sys.stderr.write("No such file: `{:}'\n".format(filename))
            except BadInstructionOrSyntax, e:
                print('File contains errors:\n{:}'.format(e.message))
            except Exception, e:
                self.exception_handler(e)
        else:
            print("Please supply a filename to read")

    def reset(self):
        if hasattr(self, "_program_text"):
            del self._program_text
        if hasattr(self, "_program_name"):
            del self._program_name
        self.simulation.reset(self)

    def add_breakpoint(self, point):
        # Load the jump table so we can match a label if present.
        if hasattr(self, "_program_text"):
            labels = self.simulation.get_assembler().get_jump_table()
            offset = self._program_text[2][0]
            if labels.has_key(point):
                point = (labels[point] * 4) + offset

        # Print info iff debugging.
        if self.local_DEBUG >= 2:
            try:
                print("DEBUG: breakpoint is {:}".format(hex(point)))
            except:
                print("DEBUG: WARNING: breakpoint is {:}".format(point))

        # Call the processor to add the break point.
        self.simulation.get_processor().add_break_point(point)

    def remove_breakpoint(self, number):
        processor = self.simulation.get_processor()
        if number in range(len(processor.get_break_points())+1):
            processor.remove_break_point(number-1)

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

    def complete(self, nobreak=False):
        """Go Forever."""
        if nobreak:
            self.simulation.get_processor().set_traps_off()
        self.simulation.run(self)


    def update(self, *args, **kwargs):
        """Callback for Broadcaster object."""
        # Truncate large records
        for memento in [self.registers, self.memory, self.pipeline]:
            if len(memento) > 10:
                memento.pop(0)

        # TODO: We're fixing a double update bug with the test for prior
        # updates. We need to look this out to prevent it from propagating.
        # (2011-08-25)
        # Push the newly retrieved values
        if not self.updated:
            if kwargs.has_key('registers'):
                self.registers.append(kwargs['registers'])
            if kwargs.has_key('memory'):
                self.memory.append(kwargs['memory'])
            if kwargs.has_key('pipeline'):
                self.pipeline.append(kwargs['pipeline'])
            if self.local_DEBUG >= 2:
                print("DEBUG: {:}".format(self.get_statistics_update()))
            try:
                self.visualizer.update(self.get_statistics_update())
                self.visualizer.render()
            except AttributeError:
                pass
            self.updated = True
        else:
            self.updated = False

    def get_statistics_update(self):
        a  = self.simulation.get_monitor().get_int_prop('processor_cycles')
        ma = self.simulation.get_monitor().get_int_prop('memory_bytes_loaded')
        mb = self.simulation.get_monitor().get_int_prop('memory_bytes_stored')
        b = 2
        try:
            b = float(ma) / float(mb)
        except: pass
        ra = self.simulation.get_monitor().get_int_prop('register_reads')
        rb = self.simulation.get_monitor().get_int_prop('register_writes')
        c = 2
        try:
            c = float(ra) / float(rb)
        except: pass
        d = 0
        e = self.simulation.get_monitor().get_int_prop('processor_executed')
        f = self.simulation.get_processor().get_registers().get_utilization()
        return [a, b, c, d, e, f]

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
            raise e

    def visualize(self, args=None):
        try:
            from module.Graphics  import Visualizer
        except:
            return
        # Try to destroy the visualizer only if there is one.
        if args == "kill":
            if hasattr(self, 'visualizer'):
                self.visualizer.__del__()
                del self.visualizer
            return
        # If it doesn't exist, do the initial setup.
        if not hasattr(self, 'visualizer'):
            self.visualizer = Visualizer()
            # We need to add nodes to the graph.
            self.visualizer.add_node(0, "Cycles")
            self.visualizer.add_node(1, "Memory Ratio")
            self.visualizer.add_node(2, "Register Ratio")
            self.visualizer.add_node(3, "null")
            self.visualizer.add_node(4, "Instructions Retired")
            self.visualizer.add_node(5, "Register Utilization")
            # We will use the easy layout options.
            self.visualizer.set_edge_layout_hub()
            self.visualizer.set_text_layout_default()
            # Init sets a window title and draws the objects
            # ready to be rendered.
            self.visualizer.initialize("CLI::Visualizer (r{:}:{:})"
                                       .format(VERSION, RELEASE_NAME))
        # Update adds the data. We can do this at any time, but preferebly
        # before displaying on the screen with render.
        self.visualizer.update(self.get_statistics_update())
        self.visualizer.render()

    def edit(self, args=None):
        if hasattr(self, '_program_name'):
            try:
                import subprocess
                subprocess.call([EDITOR, self._program_name])
                print("Editing {:} with {:}"
                      .format(self._program_name, EDITOR))
                self.load(self._program_name)
            except:
                print("Couldn't load editor: {:}".format(EDITOR))

#
# Print Functions
#

    def print_program(self):
        if hasattr(self, "_program_text"):
            print("{:-<80}".format("--Program"))
            for i in range(len(self._program_text[0])):
                # print address, assembly instruction and binary
                print("{:<12}{:<24}{:}".format(hex(self._program_text[2][i]),
                                        self._program_text[0][i],
                                        bin(self._program_text[1][i],
                                           self.isize)[2:]
                                       ))
            print("{:-<80}".format(''))
        else:
            print('No program loaded')

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

        # Grab the current frame
        try:
        # Grab an old frame if rewind is requested
            r_cur = self.registers[frame]
        except IndexError:
            print("Can't rewind {:}, only {:} values stored."
                  .format(abs(frame)-1, len(self.registers)))
            return

        # Grab the last frame for reference.
        try:
            r_prv = self.registers[frame-1]
        except IndexError:
            r_prv = None

        try:
            if self.local_DEBUG > 0:
            # Print frame information for debugging.
            # Include object id and clean up the hex string.
                print("{:-<80}".format("--Registers DEBUG-Frame-{:}"
                               .format(hex(id(r_cur))[2:].replace('L', ''))))
            else:
                print("{:-<80}".format("--Registers"))
            for i in r_cur.values():
                if i>0 and i % 4 == 0:
                    print('')
                # Get the name of the register.
                name = self.registers[frame].get_number_name_mappings()[i]
                # Print name, number and hex value.
                if (r_prv != None) and (r_cur.get_value(i) != r_prv.get_value(i)):
                    print("\033[32m{:>4}[{:0>2}]:{:.>10}\033[0m"
                          .format(name[:4], i,
                          hex(r_cur.get_value(i))[2:].replace('L', ''), 8)),
                else:
                    print("{:>4}({:0>2}):{:.>10}"
                          .format(name[:4], i,
                          hex(r_cur.get_value(i))[2:].replace('L', ''), 8)),

            # Print a bottom banner.
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
            print("{:}".format(bin(value, self.isize)[2:]))
        else:
        # Frowny is the closest we're getting to an easter egg.
            print(":-(\n{:} is not a number format (d:dec, [h,x]:hex, b:bin)"
                 .format(base))

    def print_pipeline(self):
        """Formats and outputs a display of the pipeline"""
        #the if block is just a hack to make exceptions more consistent
        #print(self._program_text)
        print("{:-<80}".format('--Pipeline'))
        if len(self.pipeline[-1]) == 0:
            print(" Begin simulation to see the pipeline")
        elif hasattr(self, "_program_text"):
            for i in range(len(self.pipeline[-1])):
                if i > len(self._program_text[1]):
                # Probably some error with the program, maybe
                # not serious. Return to avoid crashing.
                    return
                # Get the assembly relating to the integer value in the pipe-
                # line
                try:
                    index = self._program_text[1].index(self.pipeline[-1][i])
                    print("Stage {:}:{:}  {:}"
                         .format(i+1,
                                 bin(int(self.pipeline[-1][i]), self.isize)[2:],
                                 self._program_text[0][index]
                                ))
                except:
                    print("Stage {:}:No data".format(i+1))
        print("{:-<80}".format(''))

    def print_memory(self, args=[]):
        """Format and print a view of the memory."""
        start = None
        end   = 10

        if len(args) > 0:
            end = args[0]

        if len(args) > 1:
            start = args[1]

        memory_slice = self.memory[-1].get_slice(end=end, start=start).items()
        hex_width    = self.word_size / 4
        print("{:-<80}".format('--Memory'))
        for address, value in sorted(memory_slice, reverse=True):
            print(" 0x{:0>}: {:}  0x{:0>}"
                 .format(hex(address, hex_width)[2:], bin(value,self.word_size)[2:],
                         hex(value, hex_width)[2:]))
            # TODO: Divide by 4 is an assumption. Review. (2011-08-17)
        print("{:-<80}".format(''))

    def print_visualization_modules(self):
        print '\n'.join(
            self.simulation.get_monitor().list_int_props())

    def print_breakpoints(self):
        breakpoints = self.simulation.get_processor().get_break_points()
        print("{:-<80}".format('--Breakpoints'))
        try:
            for i in range(len(breakpoints)):
                # Look for the offset in program text.
                try:
                    index = self._program_text[2].index(breakpoints[i])
                    # If this fails it is best to continue. Just means
                    # breakpoint doesn't exist.
                except:
                    index = None
                # Convert to hex, skip if breakpoint not present.
                try:
                    offset = hex(breakpoints[i])
                except:
                    offset = breakpoints[i]
                # Get the associated line if the index is okay.
                if index is None:
                    line = "Offset is not in code!"
                else:
                    line = self._program_text[0][index]
                print("{:}: {:.>8}  {:}".format(i+1, offset, line))
        except Exception, e:
            print("There is a problem with the debugger. Try `reset'")
            raise e
        print("{:-<80}".format(''))

#
# Documentation Functions
#

    def usage(self, args):
        usage   = {"info":"info <r[egister[s]]> -- see help for all options."}
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
            self.exit(1)
        elif DEBUG and self.local_DEBUG >= 1:
            (exc_type, exc_value, exc_traceback) = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.exit(1)
        elif DEBUG and self.local_DEBUG >= 2:
            print('Type: ' + e.__class__.__name__)
            self.exit(1)
        return




if __name__ == '__main__':
    if len(sys.argv) > 1:
        Cli(sys.argv[1])
    else:
        sys.stderr.write('Usage: cli <config package>\n')
