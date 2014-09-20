#! /usr/bin/python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.common.apenv import ApEnv
from autopilot.test.common.aptest import APtest
from autopilot.test.common.tasks import TouchfileTask, TouchfileFailTask
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.workflows.tasks.task import TaskResult, TaskState


class WorkflowTests(APtest):
    """
    Workflow Execution Tests
    """
    def test_model_parse(self):
        (model, ex) = self.get_default_model("testwf1.wf")
        self._remove_files_if_exists(model)
        try:
            self.execute_workflow(ex)
            self.ae(2, len(ex.groupset.groups))
            self.ae("canary", ex.groupset.groups[0].groupid)
            self.ae("full", ex.groupset.groups[1].groupid)
            self.ae(2, len(ex.groupset.groups[0].tasks))
            self.ae(1, len(ex.groupset.groups[1].tasks))
            self.ae("Touchfile", ex.groupset.groups[0].tasks[0].name)
            self.ae("Touchfile2", ex.groupset.groups[0].tasks[1].name)
            self.ae("Touchfile3", ex.groupset.groups[1].tasks[0].name)
        finally:
            self._remove_files_if_exists(model)

    def test_touchfile(self):
        (model, ex) = self.get_default_model("testwf1.wf")
        self._remove_files_if_exists(model)
        try:
            self.execute_workflow(ex)
            self.at(ex.success)
            for group in ex.groupset.groups:
                for task in group.tasks:
                    self.ae(TaskState.Done, task.result.state,
                            "task should be in Done state" + str(task.result.state))
                    fp = task.properties["file_path"]
                    self.at(os.path.isfile(fp))
        finally:
            self._remove_files_if_exists(model)

    def test_touchfile_failed(self):
        (model, ex) = self.get_default_model("testwf_serial_fail.wf")
        self._remove_files_if_exists(model)
        try:
            self.execute_workflow(ex)
            self.ae(False, ex.success)
            self.ae(1, len(ex.executed_groups))
            ex.rollback()
            for group in ex.groupset.groups:
                if group.groupid == "canary":
                    for task in group.tasks:
                        self.ae(TaskState.Rolledback, task.result.state, "task should be rolledback")
                        fp = task.properties["file_path"]
                        self.af(os.path.isfile(fp))
                if group.groupid == "full":
                    # this group is never executed
                     for task in group.tasks:
                        self.ae(TaskState.Initialized, task.result.state, "task should never be run")
                        fp = task.properties["file_path"]
                        self.af(os.path.isfile(fp))
        finally:
            self._remove_files_if_exists(model)

    def get_Touchfile(self, apenv, inf, wf_id, properties, workflow_state):
        return TouchfileTask("Touchfile", apenv, wf_id, inf, properties, workflow_state)

    def get_Touchfile2(self, apenv, inf, wf_id, properties, workflow_state):
        return TouchfileTask("Touchfile2", apenv, wf_id, inf, properties, workflow_state)

    def get_Touchfile3(self, apenv, inf, wf_id, properties, workflow_state):
        return TouchfileTask("Touchfile3", apenv, wf_id, inf, properties, workflow_state)

    def get_TouchfileFail(self, apenv, inf, wf_id, properties, workflow_state):
        return TouchfileFailTask("TouchfileFail", apenv, wf_id, inf, properties, workflow_state)

    def _remove_files_if_exists(self, model):
        for group in model.groupset.groups:
            for task in group.tasks:
                fp = task.properties.get("file_path")
                if os.path.isfile(fp):
                    os.remove(fp)