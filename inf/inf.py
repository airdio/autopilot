#! /usr/bin/python

import gevent


class InfResponseContext(object):
        def __init__(self, spec):
            self.spec = spec
            self.errors = []
            self.closed = False

        def close(self, new_spec=None, new_errors=None):
            if new_spec:
                self.spec = new_spec
            if new_errors:
                self.errors.extend(new_errors)
            # close after updating the spec and errors
            self.closed = True

class Inf(object):
    """
    Interface for Inf functions
    All functions should return InfResponseContext.
    """

    def serialize(self):
        return dict()

    def init_domain(self, domain_spec):
        """
        Creates a new domain, an isolated routable environment that is unique to an org
        *.dev.marketing.com OR *.prod.marketing.com
        """
        pass

    def delete_domain(self, domain_spec, delete_dependencies=False):
        """
        Clean up the cluster environment
        """
        pass

    def init_stack(self, domain_spec, stack_spec):
        """
        Initialize role environment
        """
        pass

    def provision_instances(self, domain_spec, stack_spec, instance_spec):
        """
        Provision the role as per spec
        """
        pass