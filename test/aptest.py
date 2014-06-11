#! /usr/bin/python

import os
import unittest
import simplejson
from autopilot.common.apenv import ApEnv
from autopilot.workflows.workflow_model import WorkflowModel
from autopilot.inf.aws.awsinf import AWSInf
from autopilot.inf.aws import awsutils


class APtest(unittest.TestCase):
    """ Base class for all autopilot unit tests
    """
    def ae(self, expected, actual, msg=None):
        self.assertEqual(expected, actual, msg)

    def at(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def af(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def get_default_model(self, workflow_file, wf_id="wf_id1"):
        apenv = ApEnv()
        apenv.add(wf_id, {"resolver": self})
        return WorkflowModel.loads(apenv, simplejson.dumps(simplejson.load(self.openf(workflow_file))))

    def openf(self, path):
        fp = os.path.join("resources", path)
        return open(fp)


class AWStest(APtest):

    def get_aws_inf(self):
        self.aws_access_key = os.environ["AWS_ACCESS_KEY"]
        self.aws_secret_key = os.environ["AWS_SECRET_KEY"]
        return AWSInf(aws_access_key=self.aws_access_key,
                      aws_secret_key=self.aws_secret_key)

    def delete_vpc(self, spec={}, delete_dependencies=True):
        vpc = self. _get_vpc()
        vpc_id = spec.get("vpc_id")

        if delete_dependencies:
            security_group_id = spec.get("security_group_id", None)
            subnet_id = spec.get("subnet_id", None)
            internet_gateway_id = spec.get("internet_gateway_id", None)
            route_table_id = spec.get("route_table_id", None)

            if security_group_id is not None:
                vpc.conn.delete_security_group(group_id=security_group_id)
            if subnet_id is not None:
                vpc.conn.delete_subnet(subnet_id=subnet_id)
            if route_table_id is not None:
                vpc.conn.delete_route_table(route_table_id=route_table_id)
            if internet_gateway_id is not None:
                vpc.conn.detach_internet_gateway(internet_gateway_id=internet_gateway_id, vpc_id=vpc_id)
                vpc.conn.delete_internet_gateway(internet_gateway_id=internet_gateway_id)

        vpc.conn.delete_vpc(vpc_id=vpc_id)

    def _get_ec2(self):
        return awsutils.EasyEC2(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        return awsutils.EasyVPC(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")

