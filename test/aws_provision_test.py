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
from autopilot.test.aptest import APtest
from autopilot.workflows.workflow_model import WorkflowModel
from autopilot.workflows.tasks.task import TaskResult, TaskState, TaskGroups
from autopilot.inf.aws.awsinf import AWSInf



class AwsProvisionTests(APtest):
    """
    AWS Tests
    """
    def test_simple_provision(self):
        a = AWSInf("AKIAJYAKUIVFI6CGQDPQ",
                   "mUjbq+VRLh+WC7i2oZEqGKKgeF9XVU+LHDDx8Vzn")
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "image_id": "ami-a25415cb",
            "instance_type": "m1.small",
            "count": 1,
            "subnet_id": "subnet-59143071",
            "vpc_id": "vpc-f6a76693",
        }
        a.provision(spec)


