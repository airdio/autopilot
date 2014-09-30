#! /usr/bin/python
from autopilot.common.asyncpool import taskpool
from tornado import gen
from autopilot.common import logger
from autopilot.workflows.tasks.task import TaskState


class WorkflowExecutor(object):
    """
    Executes a given workflow and manages its life cycle
    """
    def __init__(self, apenv, model):
        self.log = logger.get_workflow_logger("WorkflowExecutor")
        self.apenv = apenv
        self.model = model
        self.workflow_state = model.workflow_state
        self.inf = model.inf
        self.groupset = model.groupset
        self.executed_groups = []
        self.success = True
        self.executed = False
        self.value = self

    def execute(self):
        """
        :type: callable
        :param Any callable. Will be called when process completes
        """
        if self.executed:
            raise Exception("Execution of a workflow is only allowed once")
        execute_future = taskpool.callable_future()
        self.executed = True
        self._execute_groups(execute_future=execute_future)
        return execute_future

    @gen.engine
    def _execute_groups(self, execute_future):
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
            self.log.info(wf_id=self.model.wf_id, msg="begin group execution: {0}".format(group.groupid))
            yield gen.Task(ec.run)

            if not self._check_group_success(group):
                # if this group failed we will not execute the
                # rest of the tasks and mark the execution as
                # failed. The caller will handle the errors and
                # rollback of needed
                self.success = False
                break

            self.log.info(wf_id=self.model.wf_id, msg="finished group execution: {0}".format(group.groupid))

        self.log.info(wf_id=self.model.wf_id, msg="finished execution of all groups. Success: {0}".format(self.success))

        # Signal future
        self.log.info(wf_id=self.model.wf_id, msg="Signalling execute_future")
        execute_future(self)

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