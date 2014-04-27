#! /usr/bin/python

import gevent
from gevent import pool
from gevent import monkey
monkey.patch_all()


class GeventPool(object):
    """
    Asynchronous pool implemented by gevent
    """
    def __init__(self, size):
        self.capacity = size
        self.pool = pool.Pool(self.capacity)

    def spawn(self, func, args=None, callback=None):
        sp = GeventPool.SpawnContext(self.pool, func, args, callback)
        return sp.spawn()

    def sleep(self, seconds=0):
        gevent.sleep(seconds)

    def join(self, timeout=None):
        self.pool.join(timeout)

    class SpawnContext(object):
        """
        SpawnContext for gevent pool
        """
        def __init__(self, gpool, func, args, finalcb):
            self.finalcb = finalcb
            self.func = func
            self.args = args
            self.gpool = gpool

        def spawn(self):
            gr = self.gpool.spawn(self.func)
            gr.link(self._linkcb)

        def _linkcb(self, greenlet):
            ## Note:
            ## Greenlet._report_error has explicit traceback.print_exception
            ## and sys.stderr.write in it. So it will print an error on the
            ## screen if self.func raises an unhandled exception
            try:
                result = greenlet.get()
                self.finalcb(result, None)
            except Exception, e:
                self.finalcb(None, e)

# todo: size should come from settings
taskpool = GeventPool(10)
