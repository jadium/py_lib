'''
Created on Jul 13, 2012

@author: darnold
'''
import logging
import subprocess
import commands
import os
import sys

def getLogger(log_level):
    try:
        lgr = logger(log_level, os.environ['PYTHON_LOGGER_LOGFILE'])
        print 'returning logger with logfile: %s'%os.environ['PYTHON_LOGGER_LOGFILE']
        raise Exception
    except:
        lgr = logger(log_level, commands.getoutput('tty'))
        print 'returning logger with logfile: %s'%commands.getoutput('tty')
    return lgr

class logger():
    crash_level = {}
    logging_handler = {}

    def __init__(self, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', **kwargs):
        try:
            logging.basicConfig(level=kwargs['loglevel'], format=format, datefmt=datefmt, filename=kwargs['logfile'])
        except:
            logging.basicConfig(level=kwargs['loglevel'], format=format, datefmt=datefmt, filename=commands.getoutput('tty'))
        try:
            self.logger = logging.getLogger(kwargs['loggername'])
        except KeyError:
            self.logger = logging.getLogger(__name__)
        logging.raiseExceptions = 0
        self.crash_level['debug'] = self.logger.debug
        self.crash_level['info'] = self.logger.info
        self.crash_level['warning'] = self.logger.warning
        self.crash_level['error'] = self.logger.error
        self.crash_level['critical'] = self.logger.critical
        self.level_names = {'critical': "CRITICAL", "error": "ERROR","warning": "WARNING", "info": "INFO", "debug": "DEBUG"}

    def addHandler(self, handler):
        self.logger.addHandler(handler) 
     
    def removeHandler(self, handler):
        self.logger.addHandler(handler) 
  
    def log(self, level, statement, file_name):
        '''
        log statement at given level
        '''
        #try:
        self.crash_level[level]("[%s]::%s::%s" % (self.level_names[level], file_name, statement))
        #if level is "critical": 
        #    self.crash_level[level]( "[%s]:: %s: %s" % (self.level_names[level], file_name, "Exiting..."))
        #    sys.exit(1)
        #except:
        #    self.crash_level["debug"]("call to %s.log() failed on: %s" %(self.__class__.__name__, statement))

    def log_exe(self, cmd, crash_level=None, exception_handler=None, file_name=None):
        '''
        log and execute command, if error raise exception handler and log at crash_level
        '''
        import sys
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout =  p.stdout.read()
        stderr =  p.stderr.read()
        p.wait()
        self.crash_level["debug"]("[DEBUG]:: %s:: %s " % (file_name, cmd))
        if len(stdout):
            self.crash_level["info"]("[STDOUT]:: %s:: %s"%(file_name, stdout))
        if len(stderr):
            self.crash_level["warning"]("[STDERR]:: %s:: %s"%(file_name, stderr))
        if p.returncode == 0: 
            return output
        if exception_handler:
            raise exception_handler(retcode)
        if retcode > 0:
            if crash_level:
               self.crash_level[crash_level]("[%s]:: %s:: %s returned: %s" % (self.level_names[crash_level], file_name, str(cmd), str(retcode)))
            if exception_handler and crash_level is not "critical":
                raise exception_handler(str(cmd) + " returned " + str(retcode))
            if crash_level is "critical":
                sys.exit(retcode)

       
    def import_module(self, *args, **kwargs):
        import importlib
        lib = importlib.import_module(kwargs['lib'])
        for k, v in lib.__dict__.items():
            if callable(v):
                if 'bad_returns' in kwargs.keys() and k in kwargs['bad_returns'].keys():
                    kwargs['bad_return'] = kwargs['bad_returns'][k]
                if 'good_returns' in kwargs.keys() and k in kwargs['good_returns'].keys():
                    kwargs['good_return'] = kwargs['good_returns'][k]
                wrapper = self.__call__(**kwargs)
                lib.__dict__[k] = wrapper(v)
                del wrapper
        return lib
 
    def __call__(self, *args, **kwargs):
        accepted_kwargs = ['bad_return', 'good_return', 'class_name', 'message', 'exception_handler']
        for kwarg in accepted_kwargs:
            self.__call__.func_globals[kwarg] = None
        for item in kwargs.keys:
            if item not in accepted_kwargs: raise ValueError('%s illegal value passed to %s'%(item, __call__.func_name)
            self.__call__.func_globals[item] = kwargs[item]

        import functools
        def decorator(function):
            function_name = function.__name__
            name_string = function_name if not class_name else "%s.%s"%(class_name, function_name)
           
            @functools.wraps(function)
            def wrapper(*args, **kwargs):
                '''
                internal decorator function
                '''
                def check_result(result):
                    '''
                    compares function return value with that of the good return value and the bad return value
                    if good_return is given, then if anything other than good_return returns from the function, an error is logged
                    if bad_return is given, then if if that specific value returns from the function, an error is logged
                    '''
                    self.log('debug', 'entering check result for %s with return: %s and bad_return: %s'%(function_name, result, bad_return), name_string)
                    if (bad_return and result == bad_return) or (good_return and result != good_return):
                        if not message:
                            self.log(kwargs['level'], "%s returned %s, this is an error!!!"%(function_name, result), name_string)
                        else:
                            self.log(kwargs['level'], "%s returned %s, this is an error!!!%s"%(function_name, result, message), name_string)
                        if exception_handler:
                            raise exception_handler('%s returned %s'%(name_string, result))
                    return result

                try:
                    os.environ['PYTHON_LOGGER_ENABLE']
                except:
                    return check_result(function(*args, **kwargs))

                self.log('debug', 'ENTERING:  %s'%function_name, name_string)
                self.log('debug', 'ARGS: %s'%", ".join([str(arg) for arg in args]), name_string)
                for k, v in kwargs.items():
                    self.log('debug', "kwargs['%s'] = %s"%(k, v), name_string)
                result = check_result(function(*args, **kwargs)
                self.log('debug', '%s returned %s'%(function_name, result), name_string)
                return result
            return wrapper
        return decorator
