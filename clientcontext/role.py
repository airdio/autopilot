#! /usr/bin python


class Role(object):
    """ Represents a role
    """
    def __init__(self, name, version, instances=1):
        self.name = name
        self.version = version
        self.instances = instances