#! /usr/bin python


class Stack(object):
    """ Represents a Stack object
    """

    def __init__(self, name, version, roles={}, vcs=None, vcs_url=None):
        #roles dictionary
        self.name = name
        self.version = version
        self.roles = roles
        self.vcs = vcs
        self.vcs_url = vcs_url

class Role(object):
    """ Represents a role
    """

    def __init__(self, name, version, instances=1):
        self.name = name
        self.version = version
        self.instances = instances