#! /usr/bin python

from tornado import gen
from autopilot.common.apenv import ApEnv
from autopilot.workflows.tasks.taskstack import Taskstack
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState


class WorkflowExecutor(object):
    """
    Executes a given workflow
    and manages its life cycle
    """
    def __init__(self, model):
        self.model = model
        self.taskset = self.model.taskset
        self.tracker = Taskstack()
        self.success = False
        self.exceptions = []
        self.executed_once = False

    def execute(self):
        if self.executed_once:
            #raise WorkflowRentrantException(self.model)
            pass
        self.executed_once = True
        if self.taskset.parallel:
            self._execute_parallel()
        else:
            self._execute_serial()

    @gen.engine
    def _execute_serial(self):
        group_count = len(self.taskset.groups)
        groups_finished = 0
        for group in self.taskset.groups:
            #track each group so that we can rollback if needed
            self.tracker.push(group)
            # this will yield to gen.engine
            # gen.engine will continue execution once task callback
            # function is executed
            try:
                yield gen.Task(self._execute_parallel, group.tasks)
                groups_finished += 1
                if group_count == groups_finished:
                    self.success = True
            except Exception, e:
                # catch all and
                self.success = False
                #send event
                #debg logging
                break

        #send notification of the result
        self._cleanup()

    def _execute_parallel(self, tasks, callback):
        pass


    def _cleanup(self):
        if self.success:
            # post status along with logs and exceptions
            pass
        else:
            self.tracker.rewind()

    def _notify(self):
        pass

