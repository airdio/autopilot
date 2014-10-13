#! /usr/bin python

import logging
import logging.handlers


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class ApLogger(object):
    """
    Base logger
    """
    def __init__(self, pylogger):
        self.logger = pylogger

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
    def __init__(self, pylogger):
        self.logger = pylogger

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


def get_logger(name=None):
    if not name:
        return logging.getLogger()
    return logging.getLogger(name)


def get_workflow_logger(name=None):
    if not name:
        return WfLogger(get_logger("Workflow"))
    return WfLogger(get_logger(name))


def get_test_logger():
    testlogger = logging.getLogger('aptest')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    ch.setFormatter(formatter)
    testlogger.addHandler(ch)
    return  testlogger

def _setup_parent_logger(console=False):
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    if console:
        ch = logging.StreamHandler()
    else:
        ch = logging.FileHandler('/tmp/autopilot.log')
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

_setup_parent_logger()
log = ApLogger(get_logger("Autopilot"))
wflog = get_workflow_logger("Workflow")
aglog = ApLogger(get_logger("Agent"))