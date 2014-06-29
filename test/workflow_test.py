#! /usr/bin/python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import simplejson
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
        ex.execute()
        self.ae(2, len(model.taskgroups))
        self.ae("canary", model.taskgroups[0].groupid)
        self.ae("full", model.taskgroups[1].groupid)
        self.ae(2, len(model.taskgroups[0].tasks))
        self.ae(1, len(model.taskgroups[1].tasks))
        self.ae("Touchfile", model.taskgroups[0].tasks[0].name)
        self.ae("Touchfile2", model.taskgroups[0].tasks[1].name)
        self.ae("Touchfile3", model.taskgroups[1].tasks[0].name)

    def test_touchfile(self):
        (model, ex) = self.get_default_model("testwf1.wf")
        self._remove_files_if_exists(model)
        try:
            ex.execute()
            self.ae(True, ex.success)
            for group in model.groupset.groups:
                for task in group.tasks:
                    self.ae(TaskState.Done, task.result.state, "task should be in Done state")
                    fp = task.properties["file_path"]
                    self.at(os.path.isfile(fp))
        finally:
            self._remove_files_if_exists(model)

    def test_touchfile_failed(self):
        (model, ex) = self.get_default_model("testwf_serial_fail.wf")
        self._remove_files_if_exists(model)
        try:
            ex.execute()
            self.ae(False, ex.success)
            self.ae(1, len(ex.executedGroups))
            ex.rollback()
            for group in model.groupset.groups:
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

    def get_Touchfile(self, apenv, inf, wf_id, properties):
        return TouchfileTask("Touchfile", apenv, wf_id, inf, properties)

    def get_Touchfile2(self, apenv, inf, wf_id, properties):
        return TouchfileTask("Touchfile2", apenv, wf_id, inf, properties)

    def get_Touchfile3(self, apenv, inf, wf_id, properties):
        return TouchfileTask("Touchfile3", apenv, wf_id, inf, properties)

    def get_TouchfileFail(self, apenv, inf, wf_id, properties):
        return TouchfileFailTask("TouchfileFail", apenv, wf_id, inf, properties)

    def _remove_files_if_exists(self, model):
        for taskgroup in model.groupset.groups:
            for task in taskgroup.tasks:
                fp = task.properties["file_path"]
                if os.path.isfile(fp):
                    os.remove(fp)