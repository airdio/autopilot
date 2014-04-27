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


class WorkflowAsyncTaskTests(APtest):
    """
    Workflow Execution with Async tasks
    """
    def test_async_workflow_tasks(self):
        #execute the model
        model = self.get_default_model("fetch_url.wf")
        ex = model.get_executor()
        ex.execute()

        #wait for the tasks to finish
        taskpool.sleep(5)

        self.at(ex.success, "Execution should not fail")

        #get response from the tasks
        tasks = model.taskgroups[0].tasks
        filename1 = tasks[0].result.result_data["filename"]
        filename2 = tasks[0].result.result_data["filename"]

        # test if data was written to file synchronously
        data1 = float(Utils.read_file(filename1)[0])
        data2 = float(Utils.read_file(filename2)[0])
        self.at((data2 - data1) < 2, "time difference should be less than 2")

        fulltasks = model.taskgroups[1].tasks
        filename3 = fulltasks[0].result.result_data["filename"]
        data3 = float(Utils.read_file(filename3)[0])
        self.at((data3 - data1) >= 2, "time difference should be greater than or equal to 2")

    def test_async_exception(self):
        model = self.get_default_model("async_exception.wf")
        ex = model.get_executor()
        ex.execute()

        taskpool.join(2)

        self.af(ex.success, "Execution should fail")

        tasks = model.taskgroups[0].tasks
        self.ae(TaskState.Error, tasks[0].result.state)
        self.ae(1, len(tasks[0].result.exceptions))

    def create_FetchUrl(self, apenv, inf, wf_id, properties):
        return FetchUrlTask("FetchUrlTask", apenv, wf_id, inf, properties)

    def create_FetchUrl2(self, apenv, inf, wf_id, properties):
        return FetchUrlTask("FetchUrlTask2", apenv, wf_id, inf, properties)

    def create_AsyncException(self, apenv, inf, wf_id, properties):
        return tasks.AsyncExceptionTask("AsyncException", apenv, inf, wf_id, properties)
