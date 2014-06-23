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

    def spawn(self, func, callback=None, delay=0, *args,  **kwargs):
        """
        Schedule func in the gevent pool. callback() once func returns
        """
        sp = GeventPool.SpawnContext(gpool=self.pool, func=func, callback=callback, delay=delay, args=args, kwargs=kwargs)
        return sp.spawn()

    def sleep(self, seconds=0):
        gevent.sleep(seconds)

    def join(self, timeout=None):
        self.pool.join(timeout)

    class SpawnContext(object):
        """
        SpawnContext for gevent pool
        """
        def __init__(self, gpool, func, finalcb=None, delay=0, *args, **kwargs):
            self.finalcb = finalcb
            self.func = func
            self.gpool = gpool
            self.delay = delay
            self.args = args
            self.kwargs = kwargs

        def spawn(self):
            if self.delay > 0:
                gr = self._spawn_later()
            else:
                gr = self.gpool.spawn(self.func)
            gr.link(self._linkcb)

        def _spawn_later(self):
            def psuedo_later():
                gevent.sleep(seconds=self.delay)
                self.func()
            return self.gpool.spawn(psuedo_later)

        def _linkcb(self, greenlet):
            ## Note:
            ## Greenlet._report_error has explicit traceback.print_exception
            ## and sys.stderr.write in it. So it will print an error on the
            ## screen if self.func raises an unhandled exception
            try:
                result = greenlet.get()
                if self.finalcb:
                    self.finalcb(result, None)
            except Exception, e:
                if self.finalcb:
                    self.finalcb(None, e)

# todo: size should come from settings
taskpool = GeventPool(10)
