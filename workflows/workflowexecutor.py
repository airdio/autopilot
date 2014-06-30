#! /usr/bin/python

from tornado import gen
from autopilot.common.utils import Dct
from autopilot.common import exception
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.workflows.tasks.task import TaskState


class WorkflowExecutor(object):
    """
    Executes a given workflow
    and manages its life cycle
    """
    def __init__(self, apenv, model, workflow_state={}, on_group_finished=None):
        self.apenv = apenv
        self.model = model
        self.executed_groups = []
        self.success = True
        self.executed = False
        self.on_group_finished = on_group_finished
        self.workflow_state = workflow_state
        self.inf = None
        self.groupset = None

    def execute(self):
        if self.executed:
            raise Exception("Execution of a workflow is only allowed once")
        self.executed = True
        self._init()
        self._execute_groups()

    @gen.engine
    def _execute_groups(self):
        """
        Groups are always executed in a serial fashion.
        Individual tasks within groups are executed in parallel
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

    def _init(self):
        # init inf
        infresolver = self.apenv.get_inf_resolver(self.model.wf_id)
        self.inf = infresolver.resolve(self.apenv, self.model)

        # groupset
        groups = []
        for groupd in self.model.groupset:
            groups.append(self._resolve_group(groupd))
        self.groupset = GroupSet(groups)

    def _resolve_group(self, groupd):
        groupid = Dct.get(groupd, "groupid")
        tasksd = Dct.get(groupd, "tasks")
        tasks = []
        task_resolver = self.apenv.get_task_resolver(self.model.wf_id)
        for taskd in tasksd:
            tasks.append(task_resolver.resolve(Dct.get(taskd, "name"), self.apenv, self.model.wf_id,
                                               self.inf, Dct.get(taskd, "properties"), self.workflow_state))
        return Group(self.model.wf_id, self.apenv, groupid, tasks)
