#! /usr/bin python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import simplejson
from autopilot.common.apenv import ApEnv
from autopilot.test.aptest import APtest
from autopilot.test.common.tasks import TouchfileTask, TouchfileFailTask
from autopilot.workflows.workflow_model import WorkflowModel


class SerialWorkflowTest(APtest):
    """ DSL Parse tests
    """
    def test_model_parse(self):
        apenv = ApEnv()
        apenv.add("wf_id1", {"resolver": self})
        model = WorkflowModel.loads(apenv, simplejson.dumps(simplejson.load(self.openf("testwf1.wf"))))
        self.ae(1, len(model.taskset.tasks))
        self.ae(False, model.taskset.parallel)

    def test_touchfile(self):
        apenv = ApEnv()
        apenv.add("wf_id1", {"resolver": self})
        model = WorkflowModel.loads(apenv, simplejson.dumps(simplejson.load(self.openf("testwf1.wf"))))
        self._remove_files_if_exists(model)
        ex = model.get_executor()
        try:
            ex.execute()
            for task in model.taskset.tasks:
                self.af(task.rolledback, "task should not be rolledback")
                fp = task.properties["file_path"]
                self.at(os.path.isfile(fp))
        finally:
            self._remove_files_if_exists(model)

    def test_touchfile_failed(self):
        apenv = ApEnv()
        apenv.add("wf_id1", {"resolver": self})
        model = WorkflowModel.loads(apenv, simplejson.dumps(simplejson.load(self.openf("testwf_serial_fail.wf"))))
        self._remove_files_if_exists(model)
        ex = model.get_executor()

        try:
            ex.execute()
            for task in model.taskset.tasks:
                self.at(task.rolledback, "task should be rolledback")
                fp = task.properties["file_path"]
                self.af(os.path.isfile(fp))
        finally:
            self._remove_files_if_exists(model)

    def _create_Touchfile(self, apenv, cloud, wf_id, properties):
        return TouchfileTask(apenv, wf_id, cloud, properties)

    def _create_TouchfileFail(self, apenv, cloud, wf_id, properties):
        return TouchfileFailTask(apenv, wf_id, cloud, properties)

    def _remove_files_if_exists(self, model):
        for task in model.taskset.tasks:
            fp = task.properties["file_path"]
            if os.path.isfile(fp):
                os.remove(fp)