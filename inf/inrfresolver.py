#! /usr/bin/python

from autopilot.common.utils import Dct
from autopilot.inf.aws.awsinf import AWSInf


class InfResolver(object):

    def __init__(self):
        pass

    def resolve(self, apenv, target, properties):
        func = getattr(InfResolver, "_get_{0}".format(target))
        return func(self, apenv, properties)

    def _get_aws(self, apenv, properties):
        return AWSInf(properties.get("aws_access_key_id"), properties.get("aws_secret_access_key"))

