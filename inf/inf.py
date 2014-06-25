#! /usr/bin/python

import gevent


class InfResponseContext(object):
        def __init__(self, spec, errors=[]):
            self.spec = spec
            self.errors = errors
            self.closed = False

        def close(self, new_spec=None, new_errors=[]):
            if new_spec:
                self.spec = new_spec
            if new_errors:
                self.errors.extend(new_errors)
            # close after updating the spec and errors
            self.closed = True

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

    def init_cluster(self, stack_spec={}):
        """
        Create a new cluster environment. An environment is an isolated topology like dev or staging or production
        An environment is within a domain
        """
        pass

    def delete_cluster(self, stack_spec={}, delete_dependencies=False):
        """
        Clean up the cluster environment
        """
        pass

    def init_stack(self, role_spec={}):
        """
        Initialize role environment
        """
        pass

    def provision_role(self, role_spec={}, tags=[]):
        """
        Provision the role as per spec
        """
        pass