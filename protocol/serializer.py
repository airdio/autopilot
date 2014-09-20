#! /usr/bin/python

import cPickle
import jsonpickle

class Serializer(object):
    def __init__(self):
        pass

    def dump(self, message, stream):
        pass

    def load(self, stream):
        pass


class cPickleSerializer(Serializer):
    """
    Serialize the messages using cPickle
    """
    def __init__(self):
        Serializer.__init__(self)

    def load(self, stream):
        return cPickle.load(stream)

    def dump(self, stream, message):
        cPickle.dump(message, stream, protocol=-1)


class JsonPickleSerializer(Serializer):
    """
    Serialize the messages using json pickle
    """
    def __init__(self):
        Serializer.__init__(self)
        jsonpickle.set_preferred_backend('json')

    def load(self, stream):
        return jsonpickle.decode(stream.readline())

    def dump(self, stream, message):
        stream.write(jsonpickle.encode(message))
