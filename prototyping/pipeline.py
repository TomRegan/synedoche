#!/usr/bin/env python
''' pipeline.py
author:      Tom Regan <thomas.c.regan@gmail.com>
since:       2011-07-09
description: Prototype of pipelined execution.
'''

class Cpu(object):

    def __init__(self, registers, memory, api, instructions):
        self.memory    = memory.getMemory()
        self.registers = registers.getRegisters()
        self.api       = api.getApiReference(self)
        self.isa       = instructions

        self.size = instructions.getSize()
        self.pc   = map(lambda x: x['profile'] == 'pc',
                        self.registers.values()).index(True)

        self.pipeline = []
        self.pipeline_stages=['fetch','decode','execute']

    def openLog(self, logger):
        """logger:object -> ...

        Begins logging activity with the logger object passed.
        """

        self.log = CpuLogger(logger)
        self.log.buffer('created a cpu')
        self.log.buffer("pc is register {0}".format(hex(self.pc)))




    def cycle(self):

        for stage in pipeline_stages:
            call = getattr(self, stage)
            call(pipeline_stages.index(stage))
        self.pc=self.pc+1
        print self.pipeline
        print '-'*20

    def fetch(self, index):
        self.log.buffer('entering fetch stage')
        try:
            i=self.memory.getWord32(self.registers[self.pc]['value'])
            self.instructions.insert(0,i)
            print 'fetched  {0}'.format(i)
        except:
            self.pipeline.insert(0,0)
        self.log.buffer('leaving fetch stage')

    #def fieldmunge(self, instruction, signature, properties):
    #    for field in signature:
    #        (start,end) = properties
    #        d[field]=int(instruction[start:end],2)
    #    return match

    def decode(self, index):
        self.log.buffer('entering decode stage')
        try:
            i=self.pipeline[index]
            properties=self.instructions.getFormatProperties()
            signatures=self.instructions.getSignatures()
            for instruction in signatures:
                #look up instruction format mapping
                #test against those fields
                pass
                    #if set(signature.items()).intersects(set(x.items())):
            print 'decoded  {0}'.format(i)
        except:
            pass
        self.log.buffer('leaving decode stage')

    def execute(self, index):
        try:
            i=self.instructions[index]
            print 'executed {0}'.format(i)
            if len(self.instructions) >3:
                self.pipeline.pop()
        except:
            pass

if __name__ == '__main__':
    processor = Cpu()
    for i in range(13):
        processor.cycle()
