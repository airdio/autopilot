#! /usr/bin python
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState
from autopilot.workflows.tasks.task import Task


class Group(object):
    """Base class for Tasks
    """
    def __init__(self, apenv, groupid, tasks):
        self.apenv = apenv
        self.groupid = groupid
        self.tasks = tasks

    #override in derived classes
    def run(self, callback):
         for task in tasks:
            task.run(callback)

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