#! /usr/bin/python
import simplejson


class Serializer(object):
    def __init__(self):
        pass

    def serialize(self, stream, obj):
        pass

    def deserialize(self, stream):
        return None


class SimpleJsonSerializer(Serializer):
    def __init__(self):
        Serializer.__init__(self)

    def deserialize(self, stream):
        return simplejson.load(stream)

    def serialize(self, stream, obj):
        simplejson.dump(obj, stream)