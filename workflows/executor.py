#! /usr/bin python

from tornado import gen
from autopilot.common.apenv import ApEnv
from autopilot.workflows.tasks.taskstack import Taskstack
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState


class WorkflowExecutor(object):
    """ Executes a given workflow
        and manages its life cycle
    """
    def __init__(self, model):
        self.model = model
        self.taskset = self.model.taskset
        self.tracker = Taskstack()
        self.success = False

    def execute(self):
        if self.taskset.parallel:
            self._execute_parallel()
        else:
            self._execute_serial()

    @gen.engine
    def _execute_serial(self):
        task_count = len(self.taskset.tasks)
        tasks_finished = 0
        for task in self.taskset.tasks:
            #track each task so that we can rollback if needed
            self.tracker.push(task)
            # this will yield to gen.engine
            # gen.engine will continue execution once task callback
            # function is executed
            yield gen.Task(task.run)
            tasks_finished += 1

            # if all tasks are done OR a single task fails then we break
            if task.result.state == TaskState.Done:
                if task_count == tasks_finished:
                    self.success = True
                    break
            else:
                self.success = False
                break
        #senf notification of the result
        self._cleanup()

    def _execute_parallel(self):
        for task in self.taskset:
            self.tracker.push(task)

    def _cleanup(self):
        if self.success:
            pass
        else:
            self.tracker.rewind()

    def _notify(self):
        pass