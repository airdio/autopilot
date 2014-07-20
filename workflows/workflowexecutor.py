#! /usr/bin/python

from tornado import gen
from autopilot.workflows.tasks.task import TaskState


class WorkflowExecutor(object):
    """
    Executes a given workflow and manages its life cycle
    """
    def __init__(self, apenv, model, on_group_finished=None):
        self.apenv = apenv
        self.model = model
        self.on_group_finished = on_group_finished
        self.workflow_state = model.workflow_state
        self.inf = model.inf
        self.groupset = model.groupset
        self.executed_groups = []
        self.success = True
        self.executed = False

    def execute(self, wait_event=None):
        if self.executed:
            raise Exception("Execution of a workflow is only allowed once")
        self.executed = True
        self._execute_groups(wait_event=wait_event)


    @gen.engine
    def _execute_groups(self, wait_event=None):
        """
        Groups are always executed in a serial fashion.
        Individual tasks within groups maybe executed in parallel
        """
        groupset = self.groupset
        for group in groupset.groups:
            # track each group execution context so that we can rollback if needed
            # execution of tasks within the group is parallel
            ec = group.get_execution_context()
            self.executed_groups.append(ec)
            # this will yield to gen.engine
            # gen.engine will continue execution once task callback
            # function is executed
            yield gen.Task(ec.run)

            # call on group finished callback handler
            # so that the caller can handle new state created
            if self.on_group_finished:
                self.on_group_finished(group)

            if not self._check_group_success(group):
                # if this group failed we will not execute the
                # rest of the tasks and mark the execution as
                # failed. The caller will handle the errors and
                # rollback of needed
                self.success = False
                break

            print "group done:{0}".format(group.groupid)

        # if we have a wait event then signal it
        if wait_event:
            print "Calling wait event"
            wait_event.set()

    @gen.engine
    def rollback(self):
        """
        Calls rollback on the executed groups in the reverse order
        """
        for g in self.executed_groups[::-1]:
            yield gen.Task(g.rewind)

    def all_tasks_succeeded(self):
        for group in self.model.taskgroups:
            if not self._check_group_success(group):
                return False
        return True

    def _check_group_success(self, group):
        for task in group.tasks:
            if task.result.state != TaskState.Done:
                return False
        return True

    def _notify(self):
        pass