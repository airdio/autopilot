#! /usr/bin python
from autopilot.common.utils import Dct
from autopilot.cloud.aws.awscloud import AWScloud


class CloudFactory(object):
    """
    """
    @staticmethod
    def create(target, properties={}):
        k = getattr(CloudFactory, "_create_{0}".format(target))
        return k(properties)

    @staticmethod
    def _create_aws(properties={}):
        return AWScloud(Dct.get(properties, "aws_access_key_id"),
                Dct.get(properties, "aws_secret_access_key"))