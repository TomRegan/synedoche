#!/usr/bin/env python
#
# Processor Implementations.
# file           : Processor.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-07-20
# last modified  : 2011-08-07
#     2011-08-18 : Added multi-part fetch.

from Interface  import UpdateBroadcaster, LoggerClient
from Monitor    import MonitorClient
from Logger     import CpuLogger
from copy       import copy, deepcopy
from SystemCall import SystemCall

from lib.Functions import binary as bin
from lib.Functions import integer as int

class BaseProcessor(UpdateBroadcaster, LoggerClient, MonitorClient):
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
        """Returns the value of the programme counter."""
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
                         .format(self.__class__.__name__))
        self._log.buffer("pc is register {0}".format(hex(self._pc)))
        self._log.buffer("pipeline: {0}"
                         .format(", ".join(self._pipeline_stages)))
        self._log.buffer("pipeline flags: {0}"
                         .format(self._pipeline_flags.replace(' ', ', ')))

    def open_monitor(self, monitor):
        self._monitor = monitor
        self._log.buffer("attached a monitor, `{:}'"
                         .format(monitor.__class__.__name__))

class Pipelined(BaseProcessor):
    """Pipelined CPU Implementation"""

    def __init__(self, pipeline, flags, **objects):
        self._instruction_decoded={}
        self._memory    = objects['memory'].get_memory()
        self._registers = objects['registers'].get_registers()
        self._api       = objects['api'].get_api_reference(self)
        self._isa       = objects['instructions']

        self._size       = self._isa.getSize()
        self._pc         = self._registers.get_pc()
        self._word_space = self._memory.get_word_spacing()

        self._pipeline        = []
        self._pipeline_stages = pipeline
        self._pipeline_flags  = flags

        self.__special_flags = {}

        self._breakpoints = []
        self._debug       = False

        self.listeners = []

    def cycle(self):
        self._log.buffer('beginning a cycle')
        self.__special_flags['increment'] = False
        try:
            for stage in self._pipeline_stages:
                self._log.buffer('entering {0} stage'.format(stage))
                # A little string transformation to help avoid accidents.
                stagecall = '_' + stage + '_coordinator'
                try:
                # Dispatch to one of the instance's methods.
                    call = getattr(self, stagecall)
                    call(self._pipeline_stages.index(stage))
                except AttributeError, e:
                    self._log.buffer('no such pipeline stage: {:}'
                                     .format(stage))
                    raise e
                except IndexError, e:
                # Routine, particularly for first cycles.
                    self._log.buffer('{0} found nothing in the pipeline'
                                     .format(stage))
                self._log.buffer('leaving {0} stage'.format(stage))
            # Do any housekeeping.
            self.__retire_cycle()
        except Exception, e:
            self.__retire_cycle()
            self.broadcast()
            self._log.buffer('EXCEPTION {:}'.format(e.message))
            raise e
        # Update listeners.
        self.broadcast()
        self._monitor.increment('processor_cycles')
        self._log.buffer('completing a cycle')


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

        self._monitor.increment('processor_fetched')

    def _decode_coordinator(self, index):
        (format_type, name, number_of_parts) = self.__decode(index)
        self._pipeline[index].append(format_type)
        self._pipeline[index].append(name)
        self._monitor.increment('processor_decoded')
        # TODO: Review - this stalls the pipeline. (2011-08-18)
        # If it is a multi-part instruction, get all of it.
        # TRY: raising index error and dealing with instruction
        # in cycle.
        while number_of_parts > 1:
            instruction = self._pipeline[0][0]
            self._log.buffer("multi-part instruction")
            part = self.__fetch()
            instruction = self.__concatenate_instruction(
                instruction, part)
            self._pipeline[0][0] = instruction
            self._registers.increment(self._pc, self._word_space)
            number_of_parts = number_of_parts - 1

    def _execute_coordinator(self, index):
        self.__execute(index)
        self._monitor.increment('processor_executed')

    def _memory_coordinator(self, index):
        pass

    def _writeback_coordinator(self, index):
        self.__writeback(index)

    def __concatenate_instruction(self, part_0, part_1):
        part_0 = bin(part_0, self._size)
        part_1 = bin(part_1, self._size)
        self._log.buffer("concatenating {:} and {:}"
                         .format(part_0[2:], part_1[2:]))
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
        self._log.buffer("decoding {0}".format(instruction))

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
                                         .format(format_type, signature))
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
                         .format(size, instruction_name))

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
                                     int(instruction_binary[start:end], 2)))

        self._log.buffer("executing {:} ({:})"
                         .format(instruction_binary, instruction_name))

        # This next step deals with the actual state change[s] by making
        # calls to the API.
        implementation = self._isa.getImplementation()
        name           = self._pipeline[index][2]
        branch_offset  = index

        if self.__special_flags['increment']:
            branch_offset = branch_offset + 1

        sequential = True
        for method in implementation[name]:
            if sequential:
                call = getattr(self._api, method[0])
                args = method[1]
                self._log.buffer("calling {0} with {1}"
                                 .format(call.__name__, args))
                sequential = call(args,
                                  self._pipeline[index][3],
                                  branch_offset=branch_offset)
            else:
                self._log.buffer('skipping an API call')
                sequential = True
        if 'EI' in self._pipeline_flags:
            self._registers.increment(self._pc, self._word_space)
            self.__special_flags['increment'] = True

    def __writeback(self, index):
        pass

    def __retire_cycle(self):
        # Retire completed instructions.
        self.broadcast()
        if len(self._pipeline) > len(self._pipeline_stages):
            self._pipeline.pop()
        # Cooperate with any debuggery.
        if self._debug and self.get_pc_value() in self._breakpoints:
            # Call for a SigTrap
            system_call = SystemCall()
            system_call.service(16435934)

    def reset(self):
        """Reset the processor to starting values."""
        self._log.buffer('RESET performing reset')
        self._log.buffer('resetting registers')
        self._registers.reset()
        self._memory.reset()
        self._log.buffer('clearing pipeline')
        self._pipeline    = []
        self._breakpoints = []
        self._log.buffer('RESET completed')
        self.broadcast()

    def add_break_point(self, offset):
        try:
            self._log.buffer('breakpoint at {:}'.format(hex(offset)))
        except:
            self._log.buffer('WARNING: breakpoint {:}')

        self._breakpoints.append(offset)
        self._debug = True

    def remove_break_point(self, number):
        try:
            offset = self._breakpoints.pop(number)
            if len(self._breakpoints) == 0:
                self._debug = False
            self._log.buffer('breakpoint removed at {:}'
                             .format(hex(offset)))
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
