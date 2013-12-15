__author__ = 'sujeet'

class Cloud(object):
    """Base class for cloud cloud
    """

    def __init__(self, statusf=None):
        self.statusf = statusf

    def validate_environment(self):
        pass

    def provision(self, role_definition):
        """ This should return a provision handle
        """
        pass

    def get_provision_status(self, provision_handle):
        """Return provision status
        """
        pass