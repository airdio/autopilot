#! /usr/bin python

class ApEnv(object):
    """
    Collection of a roles environment metadata
    """
    def __init__(self, envd={}):
        self.env = envd.copy()

    def add(self, key, value):
        self.env[key] = value

    def get(self, key, default=None):
        return self.env.get(key, default)

