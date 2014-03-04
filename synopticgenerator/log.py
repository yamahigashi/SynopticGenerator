""" coding: utf-8 """

import logging

DEFAULT_FORMATTER = '%(asctime)s %(levelname)s %(message)s at %(pathname)s %(funcName)s'

_initialized = False
_logger = None

'''
debug
info
warn
error
critical
'''


def start(filename=None, level=logging.INFO, formatter=DEFAULT_FORMATTER):

    logging.basicConfig(level=level, format=formatter)
    '''
    global _logger
    _logger = logging.getLogger("SynopticGeneratorLogger")
    _logger.setLevel(level)

    if filename:
        file_handler = logging.FileHandler(filename=filename)
        file_handler.setFormatter(logging.Formatter(formatter))
        _logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(formatter))
    _logger.addHandler(stream_handler)

    info("hoooooo")
    #info("start logging")
    '''


def debug(*args, **kwds):
    #global _logger
    logging.debug(*args)


def info(*args, **kwds):
    #global _logger
    logging.info(*args)


def warn(*args, **kwds):
    global _logger
    logging.warn(*args)


def error(*args, **kwds):
    global _logger
    logging.error(*args)



def log(*args, **kwds):
    print args[0]
