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
    def __init__(self, pylogger, source, console=False):
        self.logger = pylogger
        self.source = source
        self.console = console

    def debug(self, msg, exc_info=None):
        self.logger.debug(msg, exc_info=exc_info)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg, exc_info=None):
        self.logger.error(msg, exc_info=exc_info)

    def critical(self, msg, exc_info=None):
        self.logger.critical(msg, exc_info=exc_info)


class WfLogger(object):
    """
    Workflow Logger
    """
    def __init__(self, aplogger):
        self.logger = aplogger

    def debug(self, msg, wf_id=None, exc_info=False):
        self.logger.debug(self._format_msg(wf_id, msg), exc_info=exc_info)

    def info(self, msg, wf_id):
        self.logger.info(self._format_msg(wf_id, msg))

    def warning(self, msg, wf_id=None, exc_info=False):
        self.logger.warning(self._format_msg(wf_id, msg), exc_info=exc_info)

    def error(self, msg, wf_id=None, exc_info=True):
        self.logger.error(self._format_msg(wf_id, msg), exc_info=exc_info)

    def critical(self, msg, wf_id=None, exc_info=True):
        self.logger.critical(self._format_msg(wf_id, msg), exc_info=exc_info)

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

_logger = _create_logger("autopilot")
log = ApLogger(_logger, source="autopilot")
wflog = WfLogger(ApLogger(_logger, source="worklflow"))
aglog = ApLogger(_logger, source="autopilot")
