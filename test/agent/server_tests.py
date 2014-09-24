#! /usr/bin/python

import os
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import requests

from autopilot.test.common.aptest import APtest
from autopilot.protocol.message import Message
from autopilot.protocol.serializer import JsonPickleSerializer
from autopilot.common.server import Server
from autopilot.common.asyncpool import taskpool


class ServerTest(APtest):
    """
    Server tests
    """
    def test_gevent_server_async(self):
        m = Message(type="stack_deploy",
                    data=dict(name="test_gevent_async"),
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler())

        (status_code, response) = clientg.get()
        self.ae(200, status_code)

    def test_gevent_server_data_object(self):
        class SomeObject(object):
            def __init__(self, value=2):
                self.value = value

        m = Message(type="stack_deploy",
                    data=SomeObject(),
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler())

        (status_code, response) = clientg.get()
        self.ae(200, status_code)

    def test_gevent_server_empty_data(self):
        m = Message(type="stack_deploy",
                    data=None,
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler())

        (status_code, response) = clientg.get()
        self.ae(200, status_code)

    def test_gevent_handled_error(self):
        m = Message(type="stack_deploy",
                    data=dict(name="test_gevent_async"),
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler(exception=Exception()))

        # server stopped check status code
        (status_code, response) = clientg.get()
        self.ae(500, status_code)

    def test_gevent_unhandled_error(self):
        m = Message(type="stack_deploy",
                    data=dict(name="test_gevent_async"),
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler(exception=Exception(), unhandled=True))

        # server stopped check status code
        (status_code, response) = clientg.get()
        self.ae(500, status_code)

    def test_gevent_bad_message_format(self):
        m = "bad_message_format"

        # schedule the client to be called after the server starts
        clientg = taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler(exception=Exception(), unhandled=True))

        # server stopped check status code
        (status_code, response) = clientg.get()
        self.ae(400, status_code)

    def _start_server(self, handler, stop_delay=3):
        s = Server(serializer=JsonPickleSerializer(), handler_resolver=lambda msg: handler)
        taskpool.spawn(func=lambda: s.stop(), delay=stop_delay)
        s.start()

    def _single_message_client(self, message):
        import StringIO
        stream = StringIO.StringIO()
        JsonPickleSerializer().dump(stream=stream, message=message)
        stream.pos=0
        r = requests.post(url="http://localhost:9191", data=stream)
        return (r.status_code, r.text)

    def _string_message_client(self, message):
        r = requests.post(url="http://localhost:9191", data=message)
        return (r.status_code, r.text)

    class DefaultAsyncHandler(object):
        def __init__(self, exception=None, unhandled=False):
            self.waiter = taskpool.new_queue()
            self.exception = exception
            self.unhandled = unhandled

        def work(self, ar, message):
            self.waiter.get(block=True, timeout=5)
            taskpool.doyield(1)
            ar(result=message, exception=self.exception)

        def process(self, message, ar):
            if self.unhandled:
                raise Exception()
            taskpool.spawn(func=self.work, args={"ar": ar, "message": message})
            taskpool.spawn(func=self.waiter.put, args={"item": 2})

