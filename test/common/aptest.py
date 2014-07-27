#! /usr/bin/python

import os
import unittest
import uuid
import simplejson
from autopilot.test.common.utils import Utils
from autopilot.common.apenv import ApEnv
from autopilot.common.asyncpool import taskpool
from autopilot.inf.inrfresolver import InfResolver
from autopilot.workflows.tasks.taskresolver import TaskResolver
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor

class APtest(unittest.TestCase):
    """ Base class for all autopilot unit tests
    """
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

    def get_default_workflow_state(self):
        stack_spec = dict(materialized=dict(domain=dict(vpc_id="vpc-5c0eab39", internet_gateway_id="igw-c96eaaac"),
                                            stack=dict(cidr="10.0.0.0/24", subnets=["subnet-434b4d6b"])))
        return dict(stack_spec=stack_spec)

    def get_default_apenv(self, wf_id):
        properties = dict(aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                          aws_secret_access_key=os.environ["AWS_SECRET_KEY"])
        apenv = ApEnv()
        apenv.add(wf_id, dict(inf=properties))
        apenv.add_task_resolver(wf_id, TaskResolver(self))
        apenv.add_inf_resolver(wf_id, InfResolver())
        return apenv

    def get_default_model(self, workflow_file, wf_id="wf_id1", workflow_state={}):
        apenv = self.get_default_apenv(wf_id=wf_id)
        model = WorkflowModel.load(apenv=apenv, wf_spec_stream=self.openf(workflow_file),
                                   workflow_state=workflow_state)
        ex = WorkflowExecutor(apenv=apenv, model=model)
        return model, ex

    def execute_workflow(self, executor, timeout=10):
        wait_event = taskpool.new_event()
        executor.execute(wait_event=wait_event)
        print "Waiting for event to signal"
        wait_event.wait(timeout=timeout)

    def get_unique_wf_id(self):
        return str(uuid.uuid4())

    def openf(self, path):
        return open(os.path.join(os.environ["AUTOPILOT_HOME"], "test/resources", path))