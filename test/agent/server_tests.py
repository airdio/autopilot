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
        class Handler(object):
            def __init__(self):
                self.waiter = taskpool.new_queue()

            def work(self, ar):
                print "work function"
                self.waiter.get(block=True, timeout=5)
                print "received work...working"
                taskpool.doyield(1)
                ar(True)

            def process(self, message, ar):
                print "processing message: {0}".format(message.type)
                taskpool.spawn(func=self.work, args={"ar": ar})
                taskpool.spawn(func=self.waiter.put, args={"item": 2})

        def client():
            print "spawning client"
            m = Message(type="stack_deploy", data=dict(name="test_gevent_async"))
            import StringIO
            stream = StringIO.StringIO()
            JsonPickleSerializer().dump(stream=stream, message=m)
            stream.pos= 0
            r = requests.post(url="http://localhost:9191", data=stream)
            print r.status_code

        # schedule the client to be called after the server starts
        taskpool.spawn(func=client)

        # start the server
        print "starting server"
        s = Server(serializer=JsonPickleSerializer(), handler_resolver=lambda msg: Handler())
        taskpool.spawn(func=lambda: s.stop(), delay=3)
        s.start()



