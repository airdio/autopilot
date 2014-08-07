#! /usr/bin/python

import autopilot.protocol.serializer


class Message(object):
    def __init__(self, type, data, headers=None):
        self.type = type
        self.data = data
        self.headers = headers

    def serialize(self, serializer):
        d = dict(type=self.type, data=self.data, headers=self.headers)
        return serializer.serialize(d)