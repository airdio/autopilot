#! /user/bin python

from autopilot.cloud.cloud import Cloud


class AWScloud(Cloud):
    """ AWS Cloud specific implementation
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, statusf=None):
        Cloud.__init__(self, statusf)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    @staticmethod
    def resolve_cloud(configd, statusf=None):
        propd = configd["cloud"]["properties"]
        return AWScloud(propd["aws_access_key_id"], propd["aws_secret_access_key"], statusf)

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