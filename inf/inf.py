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

    def init_domain(self, domain_spec={}):
        """
        Creates a new domain, an isolated routable environment that is unique to an org
        *.dev.marketing.com OR *.prod.marketing.com
        """
        pass

    def delete_domain(self, domain_spec={}, delete_dependencies=False):
        """
        Clean up the cluster environment
        """
        pass

    def init_stack(self, domain_spec, stack_spec={}):
        """
        Initialize role environment
        """
        pass

    def provision_role(self, domain_spec, stack_spec, role_spec={}, tags=[]):
        """
        Provision the role as per spec
        """
        pass