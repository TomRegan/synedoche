#!/usr/bin/env python
#
# Logging Tools.
# file           : Logger.py
# author         : Tom Regan <thomas.c.regan@gmail.com>
# since          : 2011-06-30
# last modified  : 2011-07-22


import sys
from time import time, ctime
from lib.Header  import LOG_HARD_LIMIT

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
    def buffer(self, string):
        pass
    def write(self, string):
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

    def __init__(self, filename, message=None, timed=True):
        self.filename=filename
        self.timed=timed
        self.ready=False
        self.lines=[]
        self.logfile=Logfile()

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

    def buffer(self, string, timed=True, symbol=False):
        #
        # Buffering can degrade performance substantially. LOG_HARD_SIZE
        # is a parameter set in lib.Header to control the frequency
        # of write-outs (regular writes tend to improve simulation
        # cycle rate)
        #
        if timed:
            string = self._addTime(string)
        if type(symbol) == str:
            string = self._addSymbol(string, symbol)
        self.lines.append(string)
        if sys.getsizeof(self.lines) > LOG_HARD_LIMIT:
            self.flush()

    def write(self, string, timed=True, symbol=False):
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
        if message:
            time = ctime()
            message = time + ': Logging CPU activity\n'
            self.instance.write(message)

    def buffer(self, string, timed=True):
        string= 'CPU  ' + string
        self.instance.buffer(string, symbol=None, timed=timed)

    def write(self, string, timed=True):
        string= 'CPU  ' + string
        self.instance.write(string, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class MemoryLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        if message:
            time = ctime()
            message = time + ': Logging Memory activity\n'
            self.instance.write(message)

    def buffer(self, string, timed=True):
        string= 'MEM  ' + string
        self.instance.buffer(string, symbol=None, timed=timed)

    def write(self, string, timed=True):
        string= 'MEM  ' + string
        self.instance.write(string, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class AssemblerLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        if message:
            time = ctime()
            message = time + ': Logging Memory activity\n'
            self.instance.write(message)

    def buffer(self, string, timed=True):
        string= 'INT  ' + string
        self.instance.buffer(string, symbol=None, timed=timed)

    def write(self, string, timed=True):
        string= 'INT  ' + string
        self.instance.write(string, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class RegisterLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        if message:
            time = ctime()
            message = time + ': Logging Register activity\n'
            self.instance.write(message)

    def buffer(self, string, timed=True):
        string= 'REG  ' + string
        self.instance.buffer(string, symbol=None, timed=timed)

    def write(self, string, timed=True):
        string= 'REG  ' + string
        self.instance.write(string, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class ApiLogger(Logger):
    def __init__(self, instance, message=None, timed=True):
        self.instance = instance
        if message:
            time = ctime()
            message = time + ': Logging Api activity\n'
            self.instance.write(message)

    def buffer(self, string, timed=True):
        string= 'API  ' + string
        self.instance.buffer(string, symbol=None, timed=timed)

    def write(self, string, timed=True):
        string= 'API  ' + string
        self.instance.write(string, symbol=None, timed=timed)

    def flush(self):
        self.instance.flush()

class SystemLogger(Logger):
    def __init__(self, instance, message=None):
        self.instance = instance
        if message:
            self.instance.write(message)

    def buffer(self, string, timed=False):
        string= 'SYS  ' + string
        self.instance.buffer(string, timed=timed)

    def write(self, string, timed=False):
        string= 'SYS  ' + string
        self.instance.write(string, timed=timed)

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
