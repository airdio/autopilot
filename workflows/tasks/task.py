#! /usr/bin python
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState


class Task(object):
    """Base class for Tasks
    """
    StatusAdded = 0
    StatusRollback = 1

    def __init__(self, name, cloud, wf_id, properties):
        self.name = name
        self.cloud = cloud
        self.properties = properties
        self.result = None
        self.workflow = wf_id

    def run(self, callback):
        self.result = TaskResult(self, self.workflow, TaskState.Initialized)
        self.result.update("Done", TaskState.Done)

    def rollback(self):
        pass