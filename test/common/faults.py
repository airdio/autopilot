#! /usr/bin python

import os


class FaultInjector(object):
    """
    Fault injection mechanism
    """
    def __init__(self, faultspec={}):
        self.spec = faultspec

    def apply(self):
        enabled = self.spec.get("enabled", False)
        if enabled:
            exception = self.spec.get("exception", None)
            if exception is not None:
                raise exception
