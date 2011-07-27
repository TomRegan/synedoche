#!/usr/bin/env python
#
# Processor Implementations.
# file           : Processor.py
# author         : Tom Regan (thomas.c.regan@gmail.com)
# since          : 2011-07-20
# last modified  : 2011-07-22

import Monitor

from Interface import *
from Logger    import *
from copy      import deepcopy

from lib.Functions import binary as bin
from lib.Functions import integer as int

class BaseProcessor(Loggable, UpdateBroadcaster, MonitorNode):
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
    def open_monitor(self, monitor):
        pass
    def open_log(self, logger):
        pass

class Pipelined(BaseProcessor):
    """Pipelined CPU Implementation"""

    def __init__(self, pipeline, **objects):
        self._instruction_decoded={}
        self._memory    = objects['memory'].get_memory()
        self._registers = objects['registers'].getRegisters()
        self._api       = objects['api'].getApiReference(self)
        self._isa       = objects['instructions']

        self._size       = self._isa.getSize()
        self._pc         = self._registers.getPc()
        self._word_space = self._memory.get_word_spacing()

        self._pipeline = []
        self._pipeline_stages=pipeline
        self._pipeline_flags=['FI', 'FD']

        self.__special_flags = {}

    def open_log(self, logger):
        self._log = CpuLogger(logger)
        self._log.buffer("created a cpu, `{:}'"
                         .format(self.__class__.__name__))
        self._log.buffer("pc is register {0}".format(hex(self._pc)))

    def open_monitor(self, monitor):
        self._mon = monitor
        self._log.buffer("attached a monitor, `{:}'"
                         .format(monitor.__class__.__name__))

    def cycle(self):
        self._log.buffer('beginning a cycle')
        self.__special_flags['increment'] = False
        for stage in self._pipeline_stages:
            self._log.buffer('entering {0} stage'.format(stage))
            #a little string transformation to help avoid accidents
            stagecall = '_BARS' + stage.title()
            try:
                call = getattr(self, stagecall)
                call(self._pipeline_stages.index(stage))
                if len(self._pipeline) > len(self._pipeline_stages):
                    self._pipeline.pop()
            except AttributeError, e:
                self._log.buffer('no such pipeline stage: {:}'
                                 .format(stage))
                raise e
            except IndexError, e:
                self._log.buffer('{0} found nothing in the pipeline'
                                 .format(stage))
            except Exception, e:
                self._log.buffer('EXCEPTION {:}'.format(e.message))
                raise e
            self._log.buffer('leaving {0} stage'.format(stage))
        self.broadcast()
        self._mon.increment('cycles')
        self._log.buffer('completing a cycle')

    def _BARSFetch(self, index):
        self.__fetch(index)
        if 'FD' in self._pipeline_flags:
            self.__decode(index)

    def _BARSDecode(self, index):
        if not 'FD' in self._pipeline_flage:
            self.__decode(index)

    def _BARSExecute(self, index):
        self.__execute(index)

    def _BARSMemory(self, index):
        pass

    def _BARSWriteback(self, index):
        self.__writeback(index)

    def __fetch(self, index):
        i=self._memory.get_word(self._registers.getValue(self._pc),
                                self._size)
        self._pipeline.insert(0,[i])
        if 'FI' in self._pipeline_flags:
            self._registers.increment(self._pc, self._word_space)
            self.__special_flags['increment'] = True

    def __decode(self, index):
        properties=self._isa.getFormatProperties()
        signatures=self._isa.getSignatures()
        mappings = self._isa.getFormatMapping()
        i=bin(self._pipeline[index][0],self._size)[2:]
        self._log.buffer("decoding {0}".format(i))

        test={}
        #test each type of instruction
        for type in properties:
            #against each of the relevant signatures
            for signature in signatures:
                if type in mappings[signature]:
                    test.clear()
                    #we might have to deal with a multi-field signature
                    for field in signatures[signature]:
                        start= properties[type][field][0]
                        end  = properties[type][field][1]+1
                        test[field]=int(i[start:end],2)
                    if test == signatures[signature]:
                        self._pipeline[index].append(type)
                        self._pipeline[index].append(signature)
                        self._log.buffer("decoded `{0}' type instruction, {1}"
                                         .format(type, signature))
                        return

    def __execute(self, index):
        self._pipeline[index].append({})
        i=bin(self._pipeline[index][0],self._size)[2:]
        type=self._pipeline[index][1]
        properties=self._isa.getFormatProperties()
        for field in properties[type]:
            start = properties[type][field][0]
            end   = properties[type][field][1]+1
            #because we have to read bitfields, this next line is going to
            #look a bit nasty.
            self._pipeline[index][3][field] = i[start:end]
            self._log.buffer("`{:}' is {:}"
                             .format(field, i[start:end]))

        self._log.buffer("executing {:}".format(i))
        implementation = self._isa.getImplementation()
        name = self._pipeline[index][2]
        branch_offset = index
        if self.__special_flags['increment']:
            branch_offset = branch_offset + 1
        sequential = True
        for method in implementation[name]:
            if sequential:
                call = getattr(self._api, method[0])
                args = method[1]
                self._log.buffer("calling {0} with {1}".format(call.__name__, args))
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

    def reset(self):
        """Reset the processor to starting values."""
        self._log.buffer('RESET performing reset')
        self._log.buffer('resetting registers')
        self._registers.reset()
        self._memory.reset()
        self._log.buffer('clearing pipeline')
        self._pipeline=[]
        self._log.buffer('RESET completed')
        self.broadcast()

    def get_registers(self):
        return self._registers

    def get_memory(self):
        return self._memory

    def get_pipeline(self):
        return [i[0] for i in self._pipeline]
        #return self._pipeline

    def broadcast(self):
        """Overrides broadcast in the base class

        Sends information about registers, memory and pipeline.
        """
        registers = self.get_registers()
        memory    = self.get_memory()
        pipeline  = self.get_pipeline()
        super(Pipelined, self).broadcast(registers=registers,
                                         memory=memory,
                                         pipeline=pipeline)

    def register(self, listener):
        """Overrides register in the base class

        Overcomes a potential problem where newly-registered
        listeners try to query before they should and have
        to eat an eception by updating them early.
        """
        if not listener in self._listeners:
            self._listeners.append(listener)
        self.broadcast
