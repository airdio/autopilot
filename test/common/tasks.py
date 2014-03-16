#! /usr/bin python

__author__ = 'sujeet'

import os
from autopilot.workflows.tasks.task import Task
from autopilot.workflows.tasks.taskresult import TaskState


class TouchfileFailTask(Task):
    def __init__(self, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, "Touchfile", wf_id, cloud, properties)
        self.file_name = self.properties["file_path"]

    def run(self, callback):
        raise Exception("exception from TouchFileFailTask")

    def rollback(self, callback):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        Task.rollback(self, callback)

class TouchfileTask(Task):
    def __init__(self, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, "Touchfile", wf_id, cloud, properties)
        self.file_name = self.properties["file_path"]

    def run(self, callback):
        f = open(self.file_name, 'w')
        f.close()
        self.result.update("Done", TaskState.Done)
        callback(self)

    def rollback(self, callback):
        os.remove(self.file_name)
        Task.rollback(self, callback)
