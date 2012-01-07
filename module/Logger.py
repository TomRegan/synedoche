#!/usr/bin/env python
#
# Logging Tools.
# file           : Logger.py
# author         : Tom Regan <code.tregan@gmail.com>
# since          : 2011-06-30
# last modified  : 2011-07-22


import sys
from time import time, ctime
from lib.Header  import LOG_HARD_LIMIT, LOGGING_LEVEL

class level(object):
    NONE   = 0
    OFF    = 0
    ERROR  = 1
    INFO   = 2
    FINE   = 3
    FINER  = 4
    FINEST = 5
    title_of = ["NONE", "ERROR", "INFO", "FINE", "FINER", "FINEST"]

class Logfile(object):
    def open(self, filename, string):
        pass
    def close(self):
        pass
    def writelines(self, string):
        pass
    def write(self, string):
        pass


class BaseLogger(object):
    def __init__(self):
        self.filename=None
        self.timed=None
        self.ready=None
        self.lines=None
        self.instance=None
    def buffer(self, string, logging=level.ERROR):
        pass
    def write(self, string, logging=level.ERROR):
        pass
    def flush(self):
        pass
    def get_log(self):
        return self


class Logger(BaseLogger):
    """Logger(filename, [message=None, timed=False]) -> Logger

    Example usage:
        spam_log = DerrivedLogger('spam.log', 'I'm logging spam!', timed=True)
        spam_log.buffer('spam')
        spam_log.buffer('eggs')
        spam_log.flush()
        spam_log.write('spam, spam, eggs and spam')

    Resulting logfile:
        'spam.log' ->
        1| I'm logging spam!
        2| 1234567.89 spam
        3| 1234567.90 eggs
        4| 1234567.93 spam, spam, eggs and spam
    """

    def __init__(self, filename, logging=False, message=None, timed=True):
        self.filename=filename
        self.timed=timed
        self.ready=False
        self.lines=[]
        self.logfile=Logfile()
        self.logging_level = logging and logging or LOGGING_LEVEL

        try:
            self.logfile = open(filename, 'a')
            if message:
                self.logfile.write(message)
            self.ready=True
            self.logfile.close()
        except IOError as (clobber, detail):
            sys.stderr.write("Logging error: {0} opening `{1}'\nContinuing without logging.\n"
                             .format(detail.lower(),self.filename))
            pass
        except Exception as detail:
            sys.stderr.write("Logging error: {0} opening `{1}'\nContinuing without logging.\n"
                             .format(detail,self.filename))
            pass

    def _open(self):
        self.ready=False
        try:
            self.logfile = open(self.filename, 'a')
            self.ready=True
        except IOError as (clobber, detail):
            sys.stderr.write("Logging error: {0} opening `{1}'\nContinuing without logging.\n"
                             .format(detail.lower(),self.filename))
            pass
        except Exception as detail:
            sys.stderr.write("Logging error: {0} opening `{1}'\nContinuing without logging.\n"
                             .format(detail,self.filename))
            pass

    def _close(self):
        self.logfile.close()

    def _addLoggingLevel(self, string, logging):
        logging_level_title = level.title_of[logging]
        string = '{:6}  {:}'.format(logging_level_title, string)
        return string


    def _addTime(self, string):
        now = '{0:.16}'.format(time()).replace('.','')
        now = now.ljust(16,'0')
        string = '{0}:  {1}'.format(now,string)
        return string

    def _addSymbol(self, string, symbol):
        string = symbol + string
        return string

    def flush(self):
        if self.ready and len(self.lines) > 0:
            self._open()
            self.logfile.writelines('\n'.join(self.lines))
            self.logfile.write('\n')
            self._close()
            self.lines=[]

    def buffer(self, string, logging=level.ERROR, timed=True, symbol=False):
        #
        # Buffering can degrade performance substantially. LOG_HARD_SIZE
        # is a parameter set in lib.Header to control the frequency
        # of write-outs (regular writes tend to improve simulation
        # cycle rate)
        #

        string = self._addLoggingLevel(string, logging)
        if timed:
            string = self._addTime(string)
        if type(symbol) == str:
            string = self._addSymbol(string, symbol)
        self.lines.append(string)
        if sys.getsizeof(self.lines) > LOG_HARD_LIMIT:
            self.flush()

    def write(self, string, logging=level.ERROR, timed=True, symbol=False):

        string = self._addLoggingLevel(string, logging)
        if self.ready:
            self.flush()
            self._open()
            if timed:
                string = self._addTime(string)
            if type(symbol) == str:
                string = self._addSymbol(string, symbol)
            string = string + '\n'
            self.logfile.write(string)
            self._close()

class CpuLogger(Logger):
    def __init__(self, instance, message=None):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            time = ctime()
            message = time + ': Logging CPU activity\n'
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'CPU  ' + string
        self.instance.buffer(string, logging, symbol=None, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'CPU  ' + string
        self.instance.write(string, logging, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class MemoryLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            time = ctime()
            message = time + ': Logging Memory activity\n'
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'MEM  ' + string
        self.instance.buffer(string, logging, symbol=None, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'MEM  ' + string
        self.instance.write(string, logging, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class AssemblerLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            time = ctime()
            message = time + ': Logging Memory activity\n'
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'ASM  ' + string
        self.instance.buffer(string, logging, symbol=None, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'ASM  ' + string
        self.instance.write(string, logging, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class RegisterLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            time = ctime()
            message = time + ': Logging Register activity\n'
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'REG  ' + string
        self.instance.buffer(string, logging, symbol=None, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'REG  ' + string
        self.instance.write(string, logging, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class ApiLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            time = ctime()
            message = time + ': Logging Api activity\n'
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'API  ' + string
        self.instance.buffer(string, logging, symbol=None, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'API  ' + string
        self.instance.write(string, logging, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class SystemLogger(Logger):
    def __init__(self, instance, message=None):
        self.instance = instance
        self.logging_level = instance.logging_level
        if message:
            self.instance.write(message)

    def buffer(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'SYS  ' + string
        self.instance.buffer(string, logging, timed=timed)

    def write(self, string, logging=level.ERROR, timed=True):

        if logging > self.logging_level:
            return

        string= 'SYS  ' + string
        self.instance.write(string, logging, timed=timed)

    def flush(self):
        self.instance.flush()

if __name__ == '__main__':
    # TODO: Write unit-tests for logger. (2011-08-22)
    # Deprecated unit testing.
    #
    import unittest
    import os

    logname = 'testLogger.log'

    class LoggerTest(unittest.TestCase):

        def setUp(self):
            self.logger=Logger(logger)

        def tearDown(self):
            try:
                os.remove(logname)
            except:
                pass

        def testLogOrdering(self):
            good_result=['MEM  mem0\n',
                         'CPU  cpu1\n',
                         'MEM  mem2\n',
                         'CPU  cpu3\n',
                         'SYS  sys4\n',
                         'INT  int5\n',
                         'CPU  cpu6\n',
                         'SYS  sys7\n']

            logger = self.logger
            cpu=CpuLogger(logger)
            mem=MemoryLogger(logger)
            ipr=AssemblerLogger(logger)
            sys=SystemLogger(logger)

            mem.buffer('mem0', timed=False)
            cpu.buffer('cpu1', timed=False)
            mem.buffer('mem2', timed=False)
            cpu.buffer('cpu3', timed=False)
            sys.buffer('sys4', timed=False)
            ipr.buffer('int5', timed=False)
            cpu.buffer('cpu6', timed=False)
            sys.buffer('sys7', timed=False)

            cpu.flush()
            logger.flush()

            f=open(logname, 'r')
            result=f.readlines()
            self.assertEquals(good_result, result)


    tests = unittest.TestLoader().loadTestsFromTestCase(LoggerTest)
    unittest.TextTestRunner(verbosity=2).run(tests)
