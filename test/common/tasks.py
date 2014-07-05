#! /usr/bin/python

import os
import urllib2
import time
from autopilot.common.asyncpool import taskpool
from autopilot.test.common.utils import Utils
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import Task, TaskState


class FetchUrlTask(Task):
    """
    Fetch data from http url
    """
    def __init__(self, taskname, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, taskname, wf_id, inf, properties, workflow_state)
        self.url = Dct.get(properties, "fetch_url", "www.google.com")

    def on_run(self, callback):
        result = urllib2.urlopen(self.url, data=None, timeout=10)
        if result.getcode() is not 200:
            raise Exception("Cannot fetch url: {0}".format(self.url))

        with Utils.open_temp_file() as f:
            f.write(str(self.starttime))
            self.result.result_data["filename"] = f.name

        callback(TaskState.Done, [], [])

    def on_rollback(self, callback):
        raise Exception("should not be called")


class SleepTask(Task):
    def __init__(self, taskname, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, taskname, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        taskpool.doyield(seconds=3)
        callback(TaskState.Done, [], [])


class TouchfileTask(Task):
    """
    Touch file
    """
    def __init__(self, taskname, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, taskname, wf_id, inf, properties, workflow_state)
        self.file_name = self.properties["file_path"]

    def on_run(self, callback):
        f = open(self.file_name, 'w')
        f.close()
        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        Rollback this task
        """
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        callback(TaskState.Rolledback, ["Task {0} rolledback".format(self.name)], [])


class TouchfileFailTask(TouchfileTask):
    """
    Touch file failed
    """
    def __init__(self, taskname, apenv, wf_id, inf, properties, workflow_state):
        TouchfileTask.__init__(self, taskname, apenv, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        callback(TaskState.Error, ["Task {0} error".format(self.name)], [])


class AsyncExceptionTask(Task):
    def __init__(self, taskname, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, taskname, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        callback(TaskState.Error, [], [Exception("Exception from AsyncExceptionTask")])