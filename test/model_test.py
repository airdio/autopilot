#! /usr/bin python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import simplejson
from autopilot.test.aptest import APtest
from autopilot.workflows.workflow_model import WorkflowModel


class ModelTest(APtest):
    """ DSL Parse tests
    """
    def test_model_parse(self):
        model = WorkflowModel.loads(simplejson.dumps(simplejson.load(open("test.apdsl"))))
        self.ae(1, len(model.taskset))

    def test_add_instance_dsl(self):
        pass
