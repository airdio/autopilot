#! /usr/bin python
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState
from autopilot.workflows.tasks.taskstack import Taskstack
from autopilot.workflows.tasks.task import Task


class Group(object):
    """
    Groups execute all tasks in parallel
    """
    def __init__(self, apenv, groupid, tasks):
        self.apenv = apenv
        self.groupid = groupid
        self.tasks = tasks
        self.taskstack = Taskstack()

    #override in derived classes
    def run(self, callback):
        for task in self.tasks:
            self.taskstack.push(task)
            task.run(callback)

    def rollback(self, callback):
        self.taskstack.rewind()