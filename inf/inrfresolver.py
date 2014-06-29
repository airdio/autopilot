#! /usr/bin/python

from autopilot.common.utils import Dct
from autopilot.inf.aws.awsinf import AWSInf


class InfResolver(object):

    def __init__(self):
        pass

    def resolve(self, apenv, model):
        target = Dct.get(model.inf, "target")
        properties = Dct.get(model.inf, "properties")
        func = getattr(InfResolver, "_get_{0}".format(target))
        return func(apenv, properties)

    def _get_aws(self, apenv, properties):
        return AWSInf(Dct.get(properties, "aws_access_key_id"),
                        Dct.get(properties, "aws_secret_access_key"))

