#! /usr/bin python


class Stack(object):
    """ Represents a Stack object
    """
    def __init__(self, name, version, roles={}, vcs=None):
        #roles dictionary
        self.name = name
        self.version = version
        self.roles = roles
        self.vcs = vcs
