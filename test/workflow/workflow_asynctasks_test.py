#! /usr/bin/python

import os
import os.path
import sys
import time
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.test.common.utils import Utils
from autopilot.test.common.tasks import FetchUrlTask, AsyncExceptionTask, SleepTask
from autopilot.test.common.aptest import APtest
from autopilot.workflows.tasks.task import TaskState


class WorkflowAsyncTaskTests(APtest):
    """
    Workflow Execution with Async tasks
    """
    def test_async_workflow_tasks(self):
        #execute the model
        (model, ex) = self.get_default_model("fetch_url.wf")
        self.execute_workflow(ex)

        self.at(ex.success, "Execution should not fail")

        #get response from the tasks
        tasks = ex.groupset.groups[0].tasks
        filename1 = tasks[0].result.result_data["filename"]
        filename2 = tasks[0].result.result_data["filename"]

        # test if data was written to file synchronously
        data1 = float(Utils.read_file(filename1)[0])
        data2 = float(Utils.read_file(filename2)[0])
        self.at((data2 - data1) < 2, "time difference should be less than 2")

        fulltasks = ex.groupset.groups[1].tasks
        filename3 = fulltasks[0].result.result_data["filename"]
        data3 = float(Utils.read_file(filename3)[0])
        self.at((data3 - data1) >= 2, "time difference should be greater than or equal to 2")

    def test_async_exception(self):
        (model, ex) = self.get_default_model("async_exception.wf")
        self.execute_workflow(ex)
        self.af(ex.success, "Execution should fail")

        tasks = ex.groupset.groups[0].tasks
        self.ae(TaskState.Error, tasks[0].result.state)
        self.ae(1, len(tasks[0].result.exceptions))

    def get_SleepTask(self, apenv, inf, wf_id, properties, workflow_state):
        return SleepTask("SleepTask", apenv, wf_id, inf, properties, workflow_state)

    def get_FetchUrl(self, apenv, inf, wf_id, properties, workflow_state):
        return FetchUrlTask("FetchUrlTask", apenv, wf_id, inf, properties, workflow_state)

    def get_FetchUrl2(self, apenv, inf, wf_id, properties, workflow_state):
        return FetchUrlTask("FetchUrlTask2", apenv, wf_id, inf, properties, workflow_state)

    def get_AsyncException(self, apenv, inf, wf_id, properties, workflow_state):
        return AsyncExceptionTask("AsyncException", apenv, inf, wf_id, properties, workflow_state)
