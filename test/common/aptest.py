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