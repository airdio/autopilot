#! /usr/bin/python

import os
import os.path
import sys
import time
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import simplejson
from autopilot.test.common.utils import Utils
from autopilot.common.asyncpool import taskpool
from autopilot.test.common import tasks
from autopilot.test.common.tasks import FetchUrlTask
from autopilot.common.apenv import ApEnv
from autopilot.test.aptest import APtest, AWStest
from autopilot.workflows.workflow_model import WorkflowModel
from autopilot.workflows.tasks.task import TaskResult, TaskState


class AwsProvisionTests(AWStest):
    """
    AWS Tests
    """
    def test_new_environment(self):
        a = self.get_aws_inf()
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
            "auth_spec": [{"protocol": "tcp", "from": 80, "to": 80},
                          {"protocol": "tcp", "from": 3306, "to": 3306}]
        }
        try:
            a.new_env(spec)
            self.at(len(spec["vpc_id"]) > 0, "vpc_id")
            self.at(len(spec["subnet_id"]) > 0, "subnet_id")
            self.at(len(spec["internet_gateway_id"]) > 0, "internet_gateway_id")
            self.at(len(spec["security_group_id"]) > 0, "security_group_id")
        finally:
            a.clean_env(spec)

    def test_instance_provision(self):
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "image_id": "ami-a25415cb",
            "instance_type": "m1.small",
            "count": 1,
            "subnet_id": "subnet-59143071",
            "vpc_id": "vpc-f6a76693",
        }




