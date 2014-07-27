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

    def debug(self, source, msg, exc_info=False):
        pass

    def info(self, source, msg):
        pass

    def warning(self, source, msg, exc_info=False):
        pass

    def error(self, source, msg, exc_info=True):
        pass

    def critical(self, source, msg, exc_info=True):
        pass

class WfLogger(object):
    """
    """
    def __init__(self, console=False):
        self.logger = WfLogger._create_logger("workflow")
        self.console = console

    def debug(self, msg, wf_id=None, exc_info=False):
        pass

    def info(self, msg, wf_id):
        self.logger.info(self._format_msg(wf_id, msg))

    def warning(self, msg, wf_id=None, exc_info=False):
        pass

    def error(self, msg, wf_id=None, exc_info=True):
        pass

    def critical(self, msg, wf_id=None, exc_info=True):
        pass

    @staticmethod
    def _format_msg(wf_id, msg):
        return dict(wf_id=wf_id, msg=msg)

    @staticmethod
    def _create_logger(name, console=False):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if console:
            ch = logging.StreamHandler()
        else:
            ch = logging.FileHandler('/tmp/autopilot.log')
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s %(name)s %(asctime)s  %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger


wflog = WfLogger()
log = ApLogger()