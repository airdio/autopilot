#! /usr/bin python

from tornado import gen
from autopilot.common.apenv import ApEnv
from autopilot.workflows.tasks.task import TaskResult, TaskState, TaskGroups


class WorkflowExecutor(object):
    """
    Executes a given workflow
    and manages its life cycle
    """
    def __init__(self, model):
        self.model = model
        self.executedGroups = []
        self.success = True
        self.executed_once = False

    def execute(self):
        if self.executed_once:
            #raise WorkflowRentrantException(self.model)
            pass
        self.executed_once = True
        self._execute_serial()

    @gen.engine
    def _execute_serial(self):
        """
        Groups are always executed in a serial fashion.
        Individual tasks within groups are executed in parallel
        """
        taskgroups = self.model.taskgroups
        for group in taskgroups:
            # track each group execution context so that we can rollback if needed
            # execution of tasks within the group is parallel
            ec = group.get_execution_context()
            self.executedGroups.append(ec)
            # this will yield to gen.engine
            # gen.engine will continue execution once task callback
            # function is executed
            yield gen.Task(ec.run)

            if not self._check_group_success(group):
                # if this group failed we will not execute the
                self.success = False
                break

    @gen.engine
    def rollback(self):
        """
        Calls rollback on the executed groups in the reverse order
        """
        for g in self.executedGroups[::-1]:
            yield gen.Task(g.rewind)

    def _all_tasks_succeeded(self):
        for group in self.model.taskgroups:
            if not self._check_group_success(group):
                return False
        return True

    def _check_group_success(self, group):
        for task in group.tasks:
            if task.result.state == TaskState.Error:
                return False
        return True

    def _notify(self):
        pass
