#! /usr/bin/python


class InfResponseContext(object):
        def __init__(self, spec, callback=None, errors=[]):
            self.spec = spec
            self.callback = callback
            self.errors = errors

        def close(self, new_spec, errors=[]):
            self.spec = new_spec
            self.errors.extend(errors)
            if self.callback is not None:
                self.callback(self)


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

    def provision_role(self, role_spec={}, tags=[], callback=None):
        """
        Provision the role as per spec
        """
        pass