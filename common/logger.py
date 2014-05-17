#! /usr/bin python

import logging
import logging.handlers

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

class ApLogger(object):
    """
    """

    def __init__(self):
        pass

    def debug(self, source, msg, flowid=None, exc_info=False):
        print msg

    def info(self, source, msg, flowid=None):
        print msg

    def warning(self, source, msg, flowid=None, exc_info=False):
        pass

    def error(self, source, msg, flowid=None, exc_info=True):
        pass

    def critical(self, source, msg, flowid=None, exc_info=True):
        pass

log = ApLogger()