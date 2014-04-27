#! /usr/bin/python

import os
import urllib2
import time
from autopilot.test.common.utils import Utils
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import AsyncTask, Task, TaskState
from autopilot.common.asyncpool import taskpool


class FetchUrlTask(AsyncTask):

    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, taskname, wf_id, cloud, properties)
        self.url = Dct.get(properties, "fetch_url", "www.google.com")

    def on_async_run(self):
        result = urllib2.urlopen(self.url, data=None, timeout=10)
        if result.getcode() is not 200:
            raise Exception("Cannot fetch url: {0}".format(self.url))

        with Utils.open_temp_file() as f:
            f.write(str(self.starttime))
            self.result.result_data["filename"] = f.name

        taskpool.sleep(2)
        return TaskState.Done, [], []

    def on_async_rollback(self):
        raise Exception("should not be called")


class TouchfileTask(Task):

    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, taskname, wf_id, cloud, properties)
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

    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        TouchfileTask.__init__(self, taskname, apenv, wf_id, cloud, properties)

    def on_run(self, callback):
        callback(TaskState.Error, ["Task {0} error".format(self.name)], [])


class AsyncExceptionTask(AsyncTask):
    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, taskname, wf_id, cloud, properties)

    def on_async_run(self):
        return TaskState.Error, [], [Exception("Exception from AsyncExceptionTask")]