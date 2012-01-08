#!/usr/bin/env python
#
# Processor Implementations.
# file           : Processor.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-07-20
# last modified  : 2011-08-19
#     2011-08-18 : Added multi-part fetch.
#     2011-08-19 : Refactored fetch and decode.

from Api        import RegisterReferenceException
from Interface  import UpdateBroadcaster, LoggerClient
from Logger     import CpuLogger
from copy       import copy, deepcopy
from System     import SystemCall

from Logger        import level
from lib.Functions import binary as bin
from lib.Functions import integer as int

class BaseProcessor(UpdateBroadcaster, LoggerClient):
    def __init__(self, registers, memory, api, instructions):
        pass
    def cycle(self):
        """Updates the processor's state"""
        pass
    def reset(self):
        """Resets the processor's state"""
        pass
    def get_registers(self):
        """Returns a reference or copy of processor registers"""
        pass
    def get_memory(self):
        """Returns a reference or copy of memory"""
        pass
    def get_pipeline(self):
        """Returns a reference or copy of processor pipeline"""
        pass
    def get_pipeline_length(self):
        """Returns the number of stages in the pipeline."""
        pass
    def get_pc_value(self):
        """Returns the value of the program counter."""
        pass
    def add_break_point(self, offset):
        """Add a breakpoint to halt execution."""
        pass
    def remove_break_point(self, number):
        """Remove a breakpoint."""
        pass
    def get_break_points(self):
        """Returns a list of breakpoints."""
        pass
    def set_traps_off(self):
        """Disables break points."""
        pass
    def open_log(self, logger):
        self._log = CpuLogger(logger)
        self._log.buffer("created a cpu, `{:}'"
                         .format(self.__class__.__name__),
                         level.INFO)
        self._log.buffer("pc is register {0}".format(hex(self._pc)),
                         level.FINE)
        self._log.buffer("pipeline: {0}"
                         .format(", ".join(self._pipeline_stages)),
                         level.INFO)
        self._log.buffer("pipeline flags: {0}"
                         .format(self._pipeline_flags.replace(' ', ', ')),
                         level.FINE)

    def open_monitor(self, monitor):
        self.log.write("Attempted to attach monitor", level.ERROR)

class Pipelined(BaseProcessor):
    """Pipelined CPU Implementation"""

    def __init__(self, pipeline, flags, **objects):
        # These are the objects which provide data for calculations.
        self._memory    = objects['memory'].get_memory()
        self._registers = objects['registers'].get_registers()
        self._api       = objects['api'].get_api_reference(self)
        self._isa       = objects['instructions']

        # System provides Signals
        self.system_call = SystemCall()

        # This data is used in calculations.
        self._size       = self._isa.getSize()
        self._pc         = self._registers.get_pc()
        self._word_space = self._memory.get_word_spacing()

        # Pipeline is a stack for storing instructions and data relating
        # to them.
        self._pipeline        = []
        self._pipeline_stages = pipeline
        self._pipeline_flags  = flags

        # Special flags control some aspects of the processor's behaviour.
        self.__special_flags = {}

        # These fields store data for the dubugger.
        self._breakpoints = []
        self._debug       = False

        # This is a list of observers.
        self.listeners = []

    def cycle(self):

        self._log.buffer('beginning a cycle', level.FINER)

        # Denotes that incrementation has taken place this cycle.
        # This is initially false.
        self.__special_flags['increment'] = False

        try:
            for stage in self._pipeline_stages:
                self._log.buffer('entering {0} stage'.format(stage),
                                 level.FINEST)

                # A little string transformation to help avoid accidents.
                stagecall = '_' + stage + '_coordinator'

                try:
                # Dispatch to one of the instance's methods.
                    call = getattr(self, stagecall)
                    call(self._pipeline_stages.index(stage))
                except AttributeError, e:
                    self._log.buffer('no such pipeline stage: {:}'
                                     .format(stage), level.ERROR)
                    raise e
                except ArithmeticError:
                    self.system_call.service(16435935)
                except RegisterReferenceException:
                    self.system_call.service(16435936)
                except IndexError, e:
                # Routine, particularly for first cycles.
                    self._log.buffer('{0} found nothing in the pipeline'
                                     .format(stage), level.FINEST)
                self._log.buffer('leaving {0} stage'.format(stage),
                                 level.FINEST)
        except Exception, e:
            self.broadcast()
            self._log.buffer('EXCEPTION {:}'.format(e.message), level.FINE)
            raise e
        finally:
            self.__retire_cycle()
        # Update listeners.
        self.broadcast()
        self._log.buffer('completing a cycle', level.FINER)


    def _fetch_coordinator(self, index):

        # Fetch an instruction.
        instruction = self.__fetch()
        self._pipeline.insert(0, [instruction])

        ### Deal with Flags ###
        # FI denotes fetch-increment on the IP, meaning the IP is
        # updated at this stage in the cycle, rather than at the end.
        if 'FI' in self._pipeline_flags:
            self._registers.increment(self._pc, self._word_space)
            self.__special_flags['increment'] = True
        # If processor is meant to fetch and decode in one step...
        if 'FD' in self._pipeline_flags:
            self._decode_coordinator(index)

    def _decode_coordinator(self, index):
        (format_type, name, number_of_parts) = self.__decode(index)
        self._pipeline[index].append(format_type)
        self._pipeline[index].append(name)
        # TODO: Review - this stalls the pipeline. (2011-08-18)
        # If it is a multi-part instruction, get all of it.
        # TRY: raising index error and dealing with instruction
        # in cycle.
        while number_of_parts > 1:
            self._log.buffer("multi-part instruction", level.FINEST)
            instruction = self._pipeline[0][0]
            part = self.__fetch()
            instruction = self.__concatenate_instruction(
                instruction, part)
            self._pipeline[0][0] = instruction
            self._registers.increment(self._pc, self._word_space)
            number_of_parts = number_of_parts - 1

    def _execute_coordinator(self, index):
        self.__execute(index)

    def _memory_coordinator(self, index):
        pass

    def _accumilate_coordinator(self, index):
        pass

    def _writeback_coordinator(self, index):
        self.__writeback(index)

    def __concatenate_instruction(self, part_0, part_1):
        part_0 = bin(part_0, self._size)
        part_1 = bin(part_1, self._size)
        self._log.buffer("concatenating {:} and {:}"
                         .format(part_0[2:], part_1[2:]), level.FINEST)
        instruction = part_0[2:] + part_1[2:]
        return int(instruction, 2)

    def __fetch(self):
        instruction = self._memory.get_word(
            self._registers.get_value(self._pc), self._size)
        return instruction

    def __decode(self, index):
        # Data required to decode instruction
        #Format-related data
        bit_ranges  = self._isa.get_format_bit_ranges()
        cycles      = self._isa.get_format_cycles()
        # Instruction-related data
        signatures  = self._isa.getSignatures()
        mappings    = self._isa.get_instruction_to_format_map()

        # Get the instruction to decode
        instruction = bin(self._pipeline[index][0],self._size)[2:]
        self._log.buffer("decoding {0}".format(instruction), level.FINER)

        # The following block identifies the instruction being decoded.
        # It tells us the instruction's format, signature and the number
        # of parts it was broken into.
        test={}
        # Test each type of instruction
        for format_type in bit_ranges:
            # against each of the relevant signatures.
            for signature in signatures:
                # Do no work at all if the instruction is obviously
                # not a candidate.
                if format_type in mappings[signature]:
                    test.clear()

                    # We might have to deal with a multi-field signature.
                    for field in signatures[signature]:
                        start= bit_ranges[format_type][field][0]
                        end  = bit_ranges[format_type][field][1]+1
                        test[field]=int(instruction[start:end],2)

                    if test == signatures[signature]:
                        number_of_parts = cycles[format_type]
                        self._log.buffer("decoded `{0}' type instruction, {1}"
                                         .format(format_type, signature),
                                         level.FINER)
                        return (format_type, signature, number_of_parts)

    def __execute(self, index):
        # A dict to hold the encoded instruction parts.
        self._pipeline[index].append({})

        # Data on the instruction format so we can decode properly.
        format_sizes      = self._isa.get_format_sizes()
        format_properties = self._isa.get_format_bit_ranges()

        # Instruction data to operate on.
        instruction_type   = self._pipeline[index][1]
        instruction_name   = self._pipeline[index][2]

        # Particularly in the case of multi-part instructions, we need
        # to ensure the correct length binary is formed. We will use the
        # format size property to achieve this.
        size = format_sizes[instruction_type]
        self._log.buffer("reading {:}b {:} instruction"
                         .format(size, instruction_name), level.FINER)

        # Finally, translate the instruction into a binary representation.
        instruction_binary = bin(self._pipeline[index][0], size)[2:]

        # Begin the execution by decoding each bit-field.
        for field in format_properties[instruction_type]:
            start = format_properties[instruction_type][field][0]
            end   = format_properties[instruction_type][field][1]+1
            self._pipeline[index][3][field] = instruction_binary[start:end]
            self._log.buffer("`{:}' is {:} ({:})"
                             .format(field,
                                     instruction_binary[start:end],
                                     int(instruction_binary[start:end], 2)),
                             level.FINEST)

        self._log.buffer("executing {:} ({:})"
                         .format(instruction_binary, instruction_name),
                         level.FINER)

        # This next step deals with the actual state change[s] by making
        # calls to the API.
        implementation = self._isa.getImplementation()
        name           = self._pipeline[index][2]
        # The branch offset is used to calculate the address of jump
        # instructions.
        branch_offset  = index

        if self.__special_flags['increment']:
            branch_offset = branch_offset + 1

        # We also need to consider the number of fetch cycles that have
        # passed and add them to the offset calculation.
        cycles = self._isa.get_format_cycles()[instruction_type] - 1
        if cycles:
            branch_offset = branch_offset + cycles
        # If an API call returns false, the sequential flag will block
        # the next call. This is used to evaluate tests.
        sequential = True
        for method in implementation[name]:
            if sequential:
                call = getattr(self._api, method[0])
                args = method[1]
                self._log.buffer("calling {0} with {1}"
                                 .format(call.__name__, args), level.FINER)
                sequential = call(args,
                                  self._pipeline[index][3],
                                  branch_offset=branch_offset)
            else:
                self._log.buffer('skipping an API call', level.FINEST)
                sequential = True
        if 'EI' in self._pipeline_flags:
            self._registers.increment(self._pc, self._word_space)
            self.__special_flags['increment'] = True

    def __writeback(self, index):
        pass

    def __retire_cycle(self):
        # Retire completed instructions.
        if len(self._pipeline) > len(self._pipeline_stages):
            self._pipeline.pop()
        self.broadcast()
        # Cooperate with any debuggery.
        if self._debug and self.get_pc_value() in self._breakpoints:
            # Call for a SigTrap
            self.system_call.service(16435934)

    def reset(self):
        """Reset the processor to starting values."""
        self._log.buffer('RESET performing reset', level.INFO)
        self._log.buffer('resetting registers', level.FINE)
        self._registers.reset()
        self._memory.reset()
        self._log.buffer('clearing pipeline', level.FINE)
        self._pipeline    = []
        self._breakpoints = []
        self._log.buffer('RESET completed', level.FINE)
        self.broadcast()

    def add_break_point(self, offset):
        try:
            self._log.buffer('breakpoint at {:}'.format(hex(offset)),
                             level.FINEST)
        except:
            self._log.buffer('WARNING: breakpoint {:}', level.ERROR)

        self._breakpoints.append(offset)
        self._debug = True

    def remove_break_point(self, number):
        try:
            offset = self._breakpoints.pop(number)
            if len(self._breakpoints) == 0:
                self._debug = False
            self._log.buffer('breakpoint removed at {:}'
                             .format(hex(offset)), level.FINEST)
        except:
            pass

    def set_traps_off(self):
        self._debug = False

    def get_registers(self):
        return self._registers

    def get_memory(self):
        return self._memory

    def get_pipeline(self):
        return [i[0] for i in self._pipeline]

    def get_pipeline_length(self):
        return len(self._pipeline_stages)

    def get_pc_value(self):
        return self._registers.get_value(self._registers.get_pc())

    def get_break_points(self):
        return self._breakpoints

    def broadcast(self):
        """Overrides broadcast in the base class.

        Sends information about registers, memory and pipeline.
        """
        registers = self.get_registers()
        memory    = self.get_memory()
        pipeline  = self.get_pipeline()
        super(Pipelined, self).broadcast(
            self.listeners,
            registers=copy(registers),
            memory=deepcopy(memory),
            pipeline=deepcopy(pipeline))

    def register(self, listener):
        """Overrides register in the base class."""
        super(Pipelined, self).register(self.listeners, listener)
        # Overcomes a potential problem where newly-registered
        # listeners try to query before they should and have
        # to eat an eception by updating them early.
        self.broadcast()

    def remove(self, listener):
        super(Pipelined, self).remove(self.listeners, listener)

# Colophon
# The soundtrack to Processor is:
# - Radiohead's Ok Computer (unrelated coincidence)
# - Dave Matthews Band's Before These Crowded Streets
# - Dntl's Life Is Full Of Possibilities
#
# Processor was written using Vi and emacs, the choice of which was dictated
# on any given day by the strength of my wrists that morning.
#
# The author would like to thank God, the Universe and Everything.
