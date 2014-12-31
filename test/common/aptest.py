#! /usr/bin/python

import os
import unittest
import uuid
from autopilot.common import logger
from autopilot.common import utils
from autopilot.common.apenv import ApEnv
from autopilot.common.asyncpool import taskpool
from autopilot.inf.inrfresolver import InfResolver
from autopilot.workflows.tasks.taskresolver import TaskResolver
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.specifications.apspec import Apspec


class APtest(unittest.TestCase):
    """ Base class for all autopilot unit tests
    """
    test_logger = logger.get_test_logger()

    def log(self, msg, error=False):
        if error:
            APtest.test_logger.error(msg=msg)
        else:
            APtest.test_logger.info(msg)

    def ae(self, expected, actual, msg=None):
        self.assertEqual(expected, actual, msg)

    def at(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def af(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def awe(self, expected, actual):
        self.ae(expected.wf_id, actual.wf_id)
        self.ae(len(expected.groupset.groups), len(actual.groupset.groups))
        agroup_names = [agroup.groupid for agroup in actual.groupset.groups for egroup in expected.groupset.groups
                        if egroup.groupid == agroup.groupid]
        self.ae(len(expected.groupset.groups), len(agroup_names))

    def pool(self, func, args={}, callback=None, delay=0, wait_timeout=0):
        gr = taskpool.spawn(func=func, args=args, callback=callback, delay=delay)
        if wait_timeout > 0:
            taskpool.doyield(seconds=wait_timeout)
        return gr

    def doyield(self, seconds=5):
        taskpool.doyield(seconds=seconds)

    def get_aws_default_workflow_state(self):
        stack_spec = dict(materialized=dict(domain=dict(vpc_id="vpc-5c0eab39", internet_gateway_id="igw-c96eaaac"),
                                            stack=dict(cidr="10.0.0.0/24", subnets=["subnet-434b4d6b"])))
        return dict(stack_spec=stack_spec)

    def get_aws_default_apenv(self, wf_id):
        properties = dict(aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                          aws_secret_access_key=os.environ["AWS_SECRET_KEY"])
        apenv = ApEnv()
        apenv.add(wf_id, dict(inf=properties))
        apenv.add_task_resolver(wf_id, TaskResolver(self))
        apenv.add_inf_resolver(wf_id, InfResolver())
        return apenv

    def get_default_apenv(self, wf_id, properties={}):
        apenv = ApEnv()
        apenv.update(properties)
        apenv.add(wf_id, dict(inf={}))
        apenv.add_task_resolver(wf_id, TaskResolver(self))
        apenv.add_inf_resolver(wf_id, InfResolver())
        return apenv

    def get_default_model(self, workflow_file, wf_id="wf_id1", workflow_state={}):
        apenv = self.get_default_apenv(wf_id=wf_id)
        model = WorkflowModel.load(apenv=apenv, wf_spec_stream=self.openf(workflow_file),
                                   workflow_state=workflow_state)
        ex = WorkflowExecutor(apenv=apenv, model=model)
        return model, ex

    def get_aws_default_model(self, workflow_file, wf_id="wf_id1", workflow_state={}):
        apenv = self.get_aws_default_apenv(wf_id=wf_id)
        model = WorkflowModel.load(apenv=apenv, wf_spec_stream=self.openf(workflow_file),
                                   workflow_state=workflow_state)
        ex = WorkflowExecutor(apenv=apenv, model=model)
        return model, ex

    def execute_workflow(self, executor, timeout=10):
        execute_future = executor.execute()
        execute_future.wait(timeout=timeout)

    def create_specs(self, sspec_file):
        Apspec.load(ApEnv(), "contoso.org", "dev.marketing.contoso.org", self.openf(sspec_file))

    def get_unique_wf_id(self):
        return str(uuid.uuid4())

    def openf(self, path):
        return open(os.path.join(os.environ["AUTOPILOT_HOME"], "test/resources", path))

    def rmdir(self, path):
        import shutil
        if os.path.exists(path):
            shutil.rmtree(path)

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def listfiles(self, path):
        return os.listdir(path)

    def resetdir(self, path):
        self.rmdir(path)
        self.mkdir(path)


    class TimeClass():
            def __init__(self):
                self.func_time = 0

            def update_time(self):
                self.func_time = utils.get_utc_now_seconds()