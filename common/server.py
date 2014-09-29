#! /usr/bin/python

from gevent import pywsgi
from autopilot.common import logger
from autopilot.common.asyncpool import taskpool
from autopilot.protocol.message import Message


class Server(object):
    """
    Server interface
    """
    def __init__(self, serializer, handler_resolver, settings={}):
        self.handler_resolver = handler_resolver
        self.serializer = serializer
        self.host = settings.get("host", "localhost")
        self.port = settings.get("port", 9191)
        self.running = False
        self.gserver = Server.GeventServer(serializer=self.serializer,
                                           handler_resolver=self.handler_resolver)

    def start(self):
        if self.running:
            return
        self.running = True
        self.gserver.start(self.host, self.port)

    def stop(self):
        self.gserver.stop()
        self.running = False

    class GeventServer(object):
        def __init__(self, serializer, handler_resolver):
            self.log = logger.get_logger("GeventServer")
            self.serializer = serializer
            self.handler_resolver = handler_resolver
            self.instance = None

        def start(self, host, port):
            self.log.info("Starting GeventServer {0}:{1}".format(host, port))
            self.instance = pywsgi.WSGIServer((host, port), self.handle_request)
            self.instance.serve_forever()

        def stop(self):
            self.log.info("Stopping Server")
            self.instance.stop()
            self.log.info("Server stopped")

        def handle_request(self, env, start_response):
            self.log.info("GEventServer received raw request on pywsgi handler")
            response_future = taskpool.new_queue()

            def finish_response(response_message):
                import StringIO
                stream = StringIO.StringIO()
                message = response_message.value
                if response_message.exception:
                    erx = response_message.exception
                    self.log.error(msg="Response message contains an exception. {0}".format(erx.message),
                                exc_info=erx)
                    start_response('500 Internal Server Error', [])
                else:
                    start_response('200 OK', [])
                    self.log.info("Finishing response for message id:{0} and type: {1} ".format(message.identifier, message.type))
                    self.serializer.dump(stream=stream, message=message)
                    stream.pos = 0
                    response_future.put(item=stream.readline())

                response_future.put(item=StopIteration)

            # try to deserialize the message.
            # If it fails we throw a bad request
            request_message = self.serializer.load(env['wsgi.input'])
            if type(request_message) is not Message:
                start_response('400 Bad Request', [])
                self.log.error(msg="Failed to deserialize request message. Bailing out")
                response_future.put(item=StopIteration)
            else:
                try:
                    # execute handler
                    ar = taskpool.new_event()
                    self.handler_resolver(request_message.type).process(request_message, ar)
                    ar.rawlink(callback=finish_response)
                except Exception as ex:
                    start_response('500 Internal Server error', [])
                    self.log.error(msg="Unhandled exception when processing message. Message id: {0}. Message type: {1}. Exception: {2}"
                                .format(request_message.identifier, request_message.type, ex.message),
                                exc_info=ex)
                    response_future.put(item=StopIteration)

            return response_future