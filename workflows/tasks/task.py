#! /usr/bin python

from autopilot.common import utils
from autopilot.common import logger

class TaskState(object):
    """
    Task states
    """
    Initialized = 0
    Started = 1
    Error = 2
    Done = 3
    Rolledback = 4
    RolledbackError = 5

    _strs = {0: "INITIALIZED",
             1: "STARTED",
             2: "ERROR",
             3: "DONE",
             4: "ROLLEDBACK",
             5: "ROLLEDBACKERROR"}

    @staticmethod
    def to_string(state):
        return TaskState._strs.get(state, "Unknown")


class TaskResult(object):
    """
    Wraps the result of a task
    This class is supposed to be used via a Task instance
    """
    def __init__(self, task, wf_id, state):
        self.tracked_task = task
        self.workflow = wf_id
        self.state = state
        self.state_change_stack = [self.state]
        self.exceptions = []
        self.messages = []
        self.result_data = {}

    def update(self, next_state, messages=[], exceptions=[]):
        self.messages.extend(messages)
        self.exceptions.extend(exceptions)
        if self.state != next_state:
            self.state = next_state
            self.state_change_stack.append(next_state)

    def serialize(self):
        pass


class Task(object):
    """
    Models a runnable task
    """
    def __init__(self, apenv, name, wf_id, inf, properties, workflow_state):
        self.log = logger.get_workflow_logger("Task")
        self.apenv = apenv
        self.name = name
        self.inf = inf
        self.properties = properties
        self.result = None
        self.wf_id = wf_id
        self.starttime = None
        self.endtime = None
        self.workflow_state = workflow_state
        self.result = TaskResult(self, self.wf_id, TaskState.Initialized)

    def serialize(self):
        return dict(name=self.name, properties={})

    # don't override this. Override process_run
    def run(self, callback=None):
        self.starttime = utils.get_utc_now_seconds()
        if self.result.state is not TaskState.Initialized:
            # todo exceptions
            raise Exception("Task {0} is not in Initialized state. State: {1}".format(self.name, self.result.state))

        def _run_callback(final_state, messages=[], exceptions=[]):
            self.log.info(wf_id=self.wf_id, msg="Executing run callback for task: {0}. Final state: {1}"
                          .format(self.name, TaskState.to_string(final_state)))
            self.result.update(final_state, messages, exceptions)
            self._finalize()
            # original callback
            if callback:
                callback(self)

        self.result.update(TaskState.Started, ["Task {0} Started".format(self.name)])

        self.log.info(wf_id=self.wf_id, msg="begin task run: {0}".format(self.name))
        try:
            self.on_run(_run_callback)
        except Exception as ex:
            self.log.error(wf_id=self.wf_id, msg="Error executing task: {0}".format(self.name), exc_info=ex)
            _run_callback(TaskState.Error, [], [ex])

    # don't override this. Override process_rollback
    def rollback(self, callback):
        # If the task never executed then
        # do not do anything
        if self.result.state == TaskState.Initialized:
            callback(self)

        def _rollback_callback(final_state, messages=[], exceptions=[]):
            self.log.info(wf_id=self.wf_id, msg="Executing rollback callback for task: {0}. Final state: {1}"
                          .format(self.name, TaskState.to_string(final_state)))
            self.result.update(final_state, messages, exceptions)
            self._finalize()
            # call the original callback
            if callback:
                callback(self)

        self.result.update(TaskState.Rolledback, ["Task {0} Started".format(self.name)])

        self.log.info(wf_id=self.wf_id, msg="begin task rollback: {0}".format(self.name))
        try:
            self.on_rollback(_rollback_callback)
        except Exception as ex:
            self.log.error(wf_id=self.wf_id, msg="Error rolling back task: {0}".format(self.name), exc_info=ex)
            _rollback_callback(TaskState.RolledbackError, [], [ex])

    # override in derived class
    def on_run(self, callback):
        # todo make NotImplementedException
        raise Exception("should not be called. Derived class should implement this")

    # override in derived classes
    def on_rollback(self, callback):
        # todo make NotImplementedException
        raise Exception("should not be called. Derived class should implement this")

    # base class helper method to finalize this task
    def _finalize(self):
        """
        notify task status
        send relevant events
        """
        self.endtime = utils.get_utc_now_seconds()
        self.log.info(wf_id=self.wf_id, msg="Task {0} done. Final state: {1}".format(self.name, TaskState.to_string(self.result.state)))