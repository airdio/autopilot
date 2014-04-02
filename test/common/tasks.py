#! /usr/bin python

import os
from autopilot.workflows.tasks.task import Task, TaskState


class TouchfileTask(Task):
    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        Task.__init__(self, apenv, taskname, wf_id, cloud, properties)
        self.file_name = self.properties["file_path"]

    def process_run(self):
        f = open(self.file_name, 'w')
        f.close()
        return TaskState.Done, ["Task {0} done".format(self.name)], []

    def process_rollback(self):
        """
        Rollback this task
        """
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)

class TouchfileFailTask(TouchfileTask):
    def __init__(self, taskname, apenv, wf_id, cloud, properties):
        TouchfileTask.__init__(self, taskname, apenv, wf_id, cloud, properties)

    def process_run(self):
        return TaskState.Error, ["Task {0} error".format(self.name)], []