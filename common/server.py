#! /usr/bin/python

from gevent import pywsgi
from autopilot.common.logger import aglog
from autopilot.common.asyncpool import taskpool



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
            self.serializer = serializer
            self.handler_resolver = handler_resolver
            self.instance = None

        def start(self, host, port):
            aglog.info("Starting GeventServer {0}:{1}".format(host, port))
            self.instance = pywsgi.WSGIServer((host, port), self.handle_request)
            self.instance.serve_forever()

        def stop(self):
            aglog.info("Stopping Server")
            self.instance.stop()
            aglog.info("Server stopped")

        def handle_request(self, env, start_response):
            aglog.info("GEventServer received raw request on pywsgi handler")
            response_future = taskpool.new_queue()

            def finish_response(response_message):
                import StringIO
                stream = StringIO.StringIO()
                message = response_message.value
                if response_message.exception:
                    erx = response_message.exception
                    aglog.error(msg="Response message contains an exception. {0}".format(erx.message),
                                exc_info=erx)
                    start_response('500 Internal Server Error', [])
                else:
                    start_response('200 OK', [])
                    aglog.info("Finishing response for message id:{0} and type: {1} ".format(message.identifier, message.type))
                    self.serializer.dump(stream=stream, message=message)
                    stream.pos = 0
                    response_future.put(item=stream.readline())

                response_future.put(item=StopIteration)

            request_message = None
            try:
                # try to deserialize the message. If it fails we throw a bad request
                request_message = self.serializer.load(env['wsgi.input'])
            except Exception as ex:
                start_response('400 Bad Request', [])
                aglog.error(msg="Failed to deserialize the message: {0}".format(ex.message), exc_info=ex)
                response_future.put(item=StopIteration)

            try:
                # execute handler
                ar = taskpool.new_event()
                self.handler_resolver(request_message.type).process(request_message, ar)
                ar.rawlink(callback=finish_response)
            except Exception as ex:
                start_response('500 Internal Server error', [])
                aglog.error(msg="Unhandled exception when processing message. Message id: {0}. Message type: {1}. Exception: {2}"
                            .format(request_message.identifier, request_message.type, ex.message),
                            exc_info=ex)
                response_future.put(item=StopIteration)

            return response_future