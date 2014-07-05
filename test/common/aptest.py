#! /usr/bin/python

import os
import unittest
import simplejson
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

    def get_default_model(self, workflow_file, wf_id="wf_id1"):
        apenv = ApEnv()
        apenv.add(wf_id, {})
        apenv.add_task_resolver(wf_id, TaskResolver(self))
        apenv.add_inf_resolver(wf_id, InfResolver())
        model = WorkflowModel.load(self.openf(workflow_file))
        ex = WorkflowExecutor(apenv, model=model)
        return model, ex

    def execute_workflow(self, executor, timeout=10):
        wait_event = taskpool.new_event()
        executor.execute(wait_event=wait_event)
        print "Waiting for event to signal"
        wait_event.wait(timeout=timeout)

    def openf(self, path):
        return open(os.path.join(os.environ["AUTOPILOT_HOME"], "test/resources", path))