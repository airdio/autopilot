#! /usr/bin/python

import os
import os.path
import sys
import time
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import simplejson
import gevent
import gevent.monkey
from autopilot.common.apenv import ApEnv
from autopilot.common.asyncpool import taskpool
from autopilot.workflows.workflow_model import WorkflowModel
from autopilot.workflows.tasks.task import TaskResult, TaskState
from autopilot.inf.aws.awsinf import AwsInfProvisionResponseContext
from autopilot.test.common.utils import Utils
from autopilot.test.common import tasks
from autopilot.test.common.tasks import FetchUrlTask
from autopilot.test.aws.awstest import AWStest

# monkey patch
gevent.monkey.patch_all()


class AwsProvisionTests(AWStest):
    """
    AWS Tests
    """
    def test_aws_provision_response_context(self):
        def update(*args, **kwargs):
            pass
        instance1 = type('', (object, ), {"state": "pending", "update": update})()
        instance2 = type('', (object, ), {"state": "success", "update": update})()
        reservation = type('', (object, ), {"instances": [instance1, instance2]})()
        response = AwsInfProvisionResponseContext({}, reservation=reservation)
        self.af(response.wait(timeout=2, interval=1))

        instance1 = type('', (object, ), {"state": "success", "update": update})()
        instance2 = type('', (object, ), {"state": "success", "update": update})()
        reservation = type('', (object, ), {"instances": [instance1, instance2]})()
        response = AwsInfProvisionResponseContext({}, reservation=reservation)
        self.at(response.wait(timeout=2, interval=1))

    def test_stack_init(self):
        a = self.get_aws_inf()
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }

        try:
            rc = a.init_stack(spec)
            self.ae(len(rc.errors), 0, "errors found")
            self.at(len(rc.spec["vpc_id"]) > 0, "vpc_id")
            self.at(len(rc.spec["internet_gateway_id"]) > 0, "internet_gateway_id")
        finally:
            self.delete_vpc(spec, delete_dependencies=True)

    def test_role_init(self):
        a = self.get_aws_inf()
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }

        try:
            rcstack = a.init_stack(spec)
            role_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "vpc_id": rcstack.spec["vpc_id"],
                "internet_gateway_id": rcstack.spec["internet_gateway_id"],
                "cidr": "10.0.0.0/24",
                "auth_spec": [{"protocol": "tcp", "from": 80, "to": 80},
                              {"protocol": "tcp", "from": 3306, "to": 3306}],
            }
            rcrole = a.init_role(role_spec)

            self.ae(len(rcrole.errors), 0, "errors found")
            self.at(len(rcrole.spec["subnet_id"]) > 0, "subnet_id")
            self.at(len(rcrole.spec["route_table_id"]) > 0, "route_table_id")
        finally:
            self.delete_vpc(rcrole.spec, delete_dependencies=True)

    def test_instance_provision(self):
        a = self.get_aws_inf()
        stack_spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }

        try:
            rcstack = a.init_stack(stack_spec)
            role_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "vpc_id": rcstack.spec["vpc_id"],
                "internet_gateway_id": rcstack.spec["internet_gateway_id"],
                "cidr": "10.0.0.0/24",
            }
            rcrole = a.init_role(role_spec)

            instance_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "image_id": "ami-a25415cb",
                "instance_type": "m1.medium",
                "instance_count": 2,
                "subnet_id": rcrole.spec["subnet_id"],
                "vpc_id": rcrole.spec["vpc_id"],
                "associate_public_ip": True,
                "auth_spec": [{"protocol": "tcp", "from": 80, "to": 80},
                              {"protocol": "tcp", "from": 3306, "to": 3306}],
            }
            rcinstances = a.provision(instance_spec)
            rcinstances.close_on_instances_ready()
            gevent.sleep(10)

        finally:
            pass
                #self.delete_vpc(rcrole.spec, delete_dependencies=True)




