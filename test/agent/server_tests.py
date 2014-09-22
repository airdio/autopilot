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
    def test_gevent_async(self):
        m = Message(type="stack_deploy",
                    data=dict(name="test_gevent_async"),
                    identifier="test_gevent_async")

        # schedule the client to be called after the server starts
        taskpool.spawn(func=self._single_message_client, args=dict(message=m))

        # start the server
        self._start_server(handler=ServerTest.DefaultAsyncHandler())

    def _start_server(self, handler, stop_delay=3):
        s = Server(serializer=JsonPickleSerializer(), handler_resolver=lambda msg: handler)
        taskpool.spawn(func=lambda: s.stop(), delay=stop_delay)
        s.start()

    def _single_message_client(self, message):
            print "spawning client"
            import StringIO
            stream = StringIO.StringIO()
            JsonPickleSerializer().dump(stream=stream, message=message)
            stream.pos= 0
            r = requests.post(url="http://localhost:9191", data=stream)
            print r.status_code

    class DefaultAsyncHandler(object):
            def __init__(self):
                self.waiter = taskpool.new_queue()

            def work(self, ar, message):
                print "work function"
                self.waiter.get(block=True, timeout=5)
                print "received work...working"
                taskpool.doyield(1)
                ar(message)

            def process(self, message, ar):
                print "processing message: {0}".format(message.type)
                taskpool.spawn(func=self.work, args={"ar": ar, "message": message})
                taskpool.spawn(func=self.waiter.put, args={"item": 2})

