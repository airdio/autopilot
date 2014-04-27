#! /user/bin python

from autopilot.inf.inf import Inf


class AWSInf(Inf):
    """ AWS Cloud specific implementation
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, statusf=None):
        Inf.__init__(self, statusf)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

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