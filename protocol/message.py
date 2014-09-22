#! /usr/bin/python


class Message(object):
    def __init__(self, type, data, headers=None, identifier=""):
        self.type = type
        self.identifier = identifier
        self.headers = headers
        self.data = data