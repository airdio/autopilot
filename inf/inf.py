#! /usr/bin/python

import gevent

class InfResponseContext(object):
        def __init__(self, spec, callback=None, errors=[]):
            self.spec = spec
            self.callback = callback
            self.errors = errors
            self.closed = False

        def close(self, new_spec=None, new_errors=[]):
            if new_spec:
                self.spec = new_spec
            if new_errors:
                self.errors.extend(new_errors)
            # close after updating the spec and errors
            self.closed = True
            if self.callback:
                self.callback(self)

        def wait(self, timeout=30, interval=1):
            """
            gevent based wait. gevent.sleep will yield
            Should mostly be used for testing. Production code should not wait
            """
            #todo: warn if called in non-dev deployments
            tries = timeout/interval
            while tries > 0 and not self.closed:
                tries -= 1
                gevent.sleep(interval)


class Inf(object):
    """
    Interface for Inf functions
    All functions should return InfResponseContext.
    """

    def init_stack(self, stack_spec={}, callback=None):
        """
        Create a new service environment. An environment is an isolated topology like dev or staging or production
        An environment is a within a domain
        """
        pass

    def clean_stack(self, stack_spec={}, delete_dependencies=False, callback=None):
        """
        Clean up the stack environment
        """
        pass

    def init_role(self, role_spec={}, callback=None):
        """
        Initialize role environment
        """
        pass

    def provision(self, role_spec={}, tags=[], callback=None):
        """
        Provision the role as per spec
        """
        pass