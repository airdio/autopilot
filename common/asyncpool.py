#! /usr/bin/python

import gevent
import gevent.event
from gevent.queue import Queue
from gevent.event import AsyncResult
from gevent import pool
from gevent import monkey

monkey.patch_all()


class CallableWaiter(AsyncResult):
    class ValueWrapper(object):
        def __init__(self, result=None, exception=None):
            self.value = result
            self.exception=exception

        def successful(self):
            return self.exception is None

    def __init__(self):
        AsyncResult.__init__(self)

    def __call__(self, result, exception=None):
        AsyncResult.__call__(self, CallableWaiter.ValueWrapper(result=result, exception=exception))


class GeventPool(object):
    """
    Asynchronous pool implemented by gevent
    """
    def __init__(self, size):
        self.capacity = size
        self.pool = pool.Pool(self.capacity)

    def new_event(self):
        return CallableWaiter()

    def new_queue(self):
        return Queue()

    def spawn(self, func, args={}, callback=None, delay=0):
        """
        Schedule func in the gevent pool. callback() once func returns
        """
        sp = GeventPool.SpawnContext(gpool=self.pool, func=func, args=args, finalcb=callback, delay=delay)
        return sp.spawn()

    def doyield(self, seconds=0):
        gevent.sleep(seconds=seconds)

    def join(self, timeout=None):
        self.pool.join(timeout)

    class SpawnContext(object):
        """
        SpawnContext for gevent pool
        """
        def __init__(self, gpool, func, args={}, finalcb=None, delay=0):
            self.finalcb = finalcb
            self.func = func
            self.gpool = gpool
            self.delay = delay
            self.args = args

        def spawn(self):
            if self.delay > 0:
                gr = self._spawn_later()
            else:
                gr = self.gpool.spawn(self.func, **self.args)
            gr.link(self._linkcb)
            return gr

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
taskpool = GeventPool(100)
