#! /usr/bin/python

import cPickle

class Serializer(object):
    def __init__(self):
        pass

    def serialize(self, obj, stream):
        pass

    def deserialize(self, stream):
        return None


class cPickleSerializer(Serializer):
    """
    Serialize the messages using cPickle
    """
    def __init__(self):
        Serializer.__init__(self)

    def deserialize(self, stream):
        return cPickle.load(stream)

    def serialize(self, stream, obj):
        cPickle.dump(obj, stream, protocol=-1)
