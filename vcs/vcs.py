#! /usr/bin python


class Vcs(object):
    """Defines interface to a version control system
    """
    def __init__(self, target, url):
        self.target = target
        self.url = url
