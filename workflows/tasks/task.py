#! /usr/bin python

from autopilot.common import utils


class TaskState(object):
    """
    Task states
    """
    Initialized = 0
    Started = 1
    Error = 2
    Done = 3
    Rolledback = 4


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
    Base class for Tasks
    """
    def __init__(self, apenv, name, wf_id, inf, properties, workflow_state):
        self.apenv = apenv
        self.name = name
        self.inf = inf
        self.properties = properties
        self.result = None
        self.workflow = wf_id
        self.finalcallback = None  # we do not have a callback yet
        self.starttime = None
        self.endtime = None
        self.workflow_state = workflow_state
        self.result = TaskResult(self, self.workflow, TaskState.Initialized)

    # don't override this. Override process_run
    def run(self, callback):
        # print "running {0} at {1}".format(self.name, datetime.datetime.utcnow() )
        self.starttime = utils.get_utc_now_seconds()
        if callback is None:
            # todo exceptions
            raise Exception("Argument callback required")
        if self.result.state is not TaskState.Initialized:
            # todo exceptions
            raise Exception("Task {0} is not in Initialized state. State: {1}".format(self.name, self.result.state))

        # todo: assigning this callback is a hack.
        # we should to create an execution context here
        self.finalcallback = callback
        self.result.update(TaskState.Started, ["Task {0} Started".format(self.name)])
        self.on_run(self._on_run_callback)

    # don't override this. Override process_rollback
    def rollback(self, callback):
        # If the task never executed then
        # do not do anything
        if self.result.state == TaskState.Initialized:
            callback(self)

        # todo: assigning this callback is a hack.
        # we should to create an execution context here
        self.finalcallback = callback
        self.on_rollback(self._on_rollback_callback)

    # override in derived class
    def on_run(self, callback):
        # todo make NotImplementedException
        raise Exception("should not be called. Derived class should implement this")

    # override in derived classes
    def on_rollback(self, callback):
        # todo make NotImplementedException
        raise Exception("should not be called. Derived class should implement this")

    def _on_run_callback(self, final_state, messages=[], exceptions=[]):
        print "Task {0} done. Final state {1}".format(self.name, final_state)
        self.result.update(final_state, messages, exceptions)
        self._finalize()
        # original callback
        self.finalcallback(self)

    def _on_rollback_callback(self, final_state, messages=[], exceptions=[]):
        self.result.update(final_state, messages, exceptions)
        self._finalize()
        # call the original callback
        self.finalcallback(self)

    # base class helper method to finalize this task
    def _finalize(self):
        """
        notify task status
        send relevant events
        """
        self.endtime = utils.get_utc_now_seconds()
        pass