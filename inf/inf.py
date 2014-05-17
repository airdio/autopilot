

class InfRequestContext(object):
        def __init__(self, original_spec, callback=None):
            self.original_spec = original_spec
            self.callback = callback

        def close(self, new_spec, errors=None):
            pass


class Inf(object):
    """Base class for cloud cloud
    """

    def __init__(self, statusf=None):
        self.statusf = statusf

    def initialize_environment(self, spec={}, callback=None):
        pass

    def provision(self, spec={}, tags=[], callback=None):
        """
        This should return a InfProvisionContext
        """
        pass