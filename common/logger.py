#! /usr/bin python

import logging
import logging.handlers


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class ApLogger(object):
    """
    Base logger.
    """
    def __init__(self, pylogger, console=False):
        self.logger = pylogger
        self.console = console

    def debug(self, source, msg, exc_info=None):
        self.logger.debug(msg, exc_info=exc_info)

    def info(self, source, msg):
        self.logger.info(msg)

    def warning(self, source, msg):
        self.logger.warning(msg)

    def error(self, source, msg, exc_info=None):
        self.logger.error(msg, exc_info=exc_info)

    def critical(self, source, msg, exc_info=None):
        self.logger.critical(msg, exc_info=exc_info)


class WfLogger(object):
    """
    Workflow Logger
    """
    def __init__(self, aplogger):
        self.logger = aplogger

    def debug(self, msg, wf_id=None, exc_info=False):
        pass

    def info(self, msg, wf_id):
        self.logger.info("Workflow", self._format_msg(wf_id, msg))

    def warning(self, msg, wf_id=None, exc_info=False):
        pass

    def error(self, msg, wf_id=None, exc_info=True):
        pass

    def critical(self, msg, wf_id=None, exc_info=True):
        pass

    def _format_msg(self, wf_id, msg):
        return dict(wf_id=wf_id, msg=msg)


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

log = ApLogger(_create_logger("autopilot"))
wflog = WfLogger(log)
