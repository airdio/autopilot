#! /usr/bin/python

import gevent
from gevent import pool
from gevent import monkey
monkey.patch_all()


class GeventPool(object):
    def __init__(self, size):
        self.capacity = size
        self.pool = pool.Pool(self.capacity)

    def spawn(self, func, args=None, callback = None):
        self.pool.spawn(func)

    def sleep(self, seconds=0):
        gevent.sleep(seconds)

    def join(self, timeout=None):
        self.pool.join(timeout)

#todo: size should come from settings
taskpool = GeventPool(10)






