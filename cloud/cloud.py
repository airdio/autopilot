__author__ = 'sujeet'

class Cloud(object):
    """Base class for cloud cloud
    """

    def __init__(self, statusf=None):
        self.statusf = statusf

    def validate_environment(self):
        pass

    def get_instance(self, instance_context, callback):
        pass

    def create_instance(self, instance_context, callback):
        """ This should return a provision handle
        """
        pass

    def register_instance_status(self, instance_context, callback):
        """Return provision status
        """
        pass