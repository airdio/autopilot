#! /usr/bin/python

from autopilot.common.utils import Dct
from autopilot.inf.aws.awsinf import AWSInf


class InFactory(object):

    @staticmethod
    def create(target, properties={}):
        k = getattr(InFactory, "_create_{0}".format(target))
        return k(properties)

    @staticmethod
    def _create_aws(properties={}):
        return AWSInf(Dct.get(properties, "aws_access_key_id"),
                        Dct.get(properties, "aws_secret_access_key"))
