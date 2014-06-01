

class InfRequestContext(object):
        def __init__(self, spec, callback=None):
            self.spec = spec
            self.callback = callback

        def close(self, new_spec, errors=None):
            pass


class Inf(object):
    """
    Interface for Inf functions
    All functions should return InfRequestContext. This is like a future since
    most of these operations will be asynchronous
    """

    def new_env(self, env_spec={}, callback=None):
        """
        Create a new service environment. An environment is an isolated topology like dev or staging or production
        An environment is a within a domain
        """
        pass

    def clean_env(self, env_spec={}, callback=None):
        """
        Clean up the environemnt
        """

    def new_instance(self, instance_spec={}, tags=[], callback=None):
        """
        Provision a new instance
        """
        pass