#! /usr/bin/python

from tornado import gen
from autopilot.common.logger import wflog
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
        self.value = self

    def execute(self, callback=None):
        """
        :type: callable
        :param Any callable. Will be called when process completes
        """
        if self.executed:
            raise Exception("Execution of a workflow is only allowed once")
        self.executed = True
        self._execute_groups(callback=callback)

    def successful(self):
        """
        Hook to make callback work is its gevent.Asyncresult
        """
        return True

    @gen.engine
    def _execute_groups(self, callback=None):
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
            wflog.info(wf_id=self.model.wf_id, msg="begin group execution: {0}".format(group.groupid))
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

            wflog.info(wf_id=self.model.wf_id, msg="finished group execution: {0}".format(group.groupid))

        wflog.info(wf_id=self.model.wf_id, msg="finished workflow execution. Sucess: {0}".format(self.success))

        # if we have a callback signal it.
        if callback:
            wflog.info(wf_id=self.model.wf_id, msg="Signalling callback")
            callback(self)

    @gen.engine
    def rollback(self):
        """
        Calls rollback on the executed groups in the reverse order
        """
        for g in self.executed_groups[::-1]:
            yield gen.Task(g.rewind)

    def _all_tasks_succeeded(self):
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