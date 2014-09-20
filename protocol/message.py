#! /usr/bin/python


class Message(object):
    def __init__(self, type, data, headers=None):
        self.type = type
        self.headers = headers
        self.data = data