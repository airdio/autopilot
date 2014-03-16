#! /usr/bin python
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState

class Task(object):
    """Base class for Tasks
    """
    def __init__(self, apenv, name, wf_id, cloud, properties):
        self.apenv = apenv
        self.name = name
        self.cloud = cloud
        self.properties = properties
        self.result = None
        self.workflow = wf_id
        self.rolledback = False
        self.result = TaskResult(self, self.workflow, TaskState.Initialized)

    #override in derived classes
    def run(self, callback):
        self.result.update("Done", TaskState.Done)
        self.callback(self)

    def rollback(self, callback):
        self.rolledback = True
        self.result.update("Rolledback", TaskState.Error)
        callback(self)

class TaskSet(object):
    """
    Set of tasks
    """
    def __init__(self, parallel, tasks=[]):
        self.parallel = parallel
        self.tasks = tasks