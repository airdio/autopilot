#! /usr/bin python

__author__ = 'sujeet'

import os
from autopilot.workflows.tasks.task import Task
from autopilot.workflows.tasks.taskresult import TaskState


class TouchfileTask(Task):
    def __init__(self, apenv, wf_id, file_name):
        Task.__init__(self, apenv, "Touchfile", wf_id, None, None)
        self.file_name = file_name
        self.fi = fi

    def run(self, callback):
        f = open(self.file_name, 'w')
        f.close()
        callback(self)

    def rollback(self):
        self.rolledback = True
        os.remove(self.file_name)
        callable(self)


class TouchfileTask2(Task):
    def __init__(self, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, "Touchfile", wf_id, cloud, properties)
        self.file_name = self.properties["file_path"]

    def run(self, callback):
        f = open(self.file_name, 'w')
        f.close()
        self.result.update("Done", TaskState.Done)
        callback(self)

    def rollback(self):
        self.rolledback = True
        os.remove(self.file_name)
        callable(self)
