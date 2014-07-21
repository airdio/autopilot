#! /usr/bin/python
from tornado import gen
from autopilot.common.asyncpool import taskpool


class Group(object):
    """
    Groups execute all tasks in parallel
    """
    def __init__(self, wf_id, apenv, groupid, tasks):
        self.wf_id = wf_id
        self.apenv = apenv
        self.groupid = groupid
        self.tasks = tasks

    def serialize(self):
        return dict(groupid=self.groupid,
                    tasks=[t.serialize() for t in self.tasks if t]
                    )

    def get_execution_context(self):
        """
        Returns a fresh execution context
        """
        return GroupExecutionContext(self.groupid, self.tasks)


class GroupSet(object):
    """
    Groups
    """
    def __init__(self, groups=[]):
        self.groups = groups

    def serialize(self):
        return [g.serialize() for g in self.groups if g]


class GroupExecutionContext(object):
    def __init__(self, groupid, tasks):
        self.groupid = groupid
        self.tasks = tasks
        self.tasksdone = 0
        self.finalcallback = None
        self.rolledback = False

    def run(self, callback):
        """
        Schedule all tasks in this group to run in parallel
        """
        self.finalcallback = callback
        for task in self.tasks:
            # schedule both the tasks to execute
            print("Spawning task:{0}".format(task.name))
            taskpool.spawn(task.run, args=dict(callback=self._task_callback))

    def _task_callback(self, task):
        self.tasksdone += 1
        if self.tasksdone == len(self.tasks):
            self.finalcallback(self.tasks)

    @gen.engine
    def rewind(self, callback):
        """
        Tasks will be rolled back in a reverse order synchronously
        """
        self.rolledback = True
        for t in self.tasks[::-1]:
            yield gen.Task(t.rollback)
        callback(self)