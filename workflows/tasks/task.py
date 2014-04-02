#! /usr/bin python

class TaskGroups(object):
    """
    Groups of tasks
    """
    def __init__(self, groups=[]):
        self.groups = groups

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
        self.notification_targets = []
        self.state_change_stack = [self.state]
        self.exceptions = []
        self.messages = []

    def update(self, next_state, messages=[], exceptions=[]):
        self.messages.append(messages)
        self.exceptions.append(exceptions)
        if self.state != next_state:
            self.state = next_state
            self.state_change_stack.append(next_state)

    def serialize(self):
        pass

class Task(object):
    """
    Base class for Tasks
    """
    def __init__(self, apenv, name, wf_id, cloud, properties):
        self.apenv = apenv
        self.name = name
        self.cloud = cloud
        self.properties = properties
        self.result = None
        self.workflow = wf_id
        self.result = TaskResult(self, self.workflow, TaskState.Initialized)

    #override in derived classes
    def run(self, callback):
        self.result.update(TaskState.Started,
                           ["Task {0} Started".format(self.name)])
        (final_state, messages, exceptions) = self.process_run()
        self.result.update(final_state, messages, exceptions)
        self._finalize()
        callback(self)

    # override in derived class
    def rollback(self, callback):
        # If the task never executed then
        # do not do anything
        if self.result.state == TaskState.Initialized:
            callback(self)

        self.process_rollback()

        self.result.update(TaskState.Rolledback, ["Rolledback"])
        self._finalize()
        callback(self)

    def process_run(self):
        return TaskState.Done, ["Task {0} done".format(self.name)], []

    def process_rollback(self):
        pass

    # base class helper method to finalize this task
    def _finalize(self):
        """
        notify the task state machine is done
        send events
        """
        pass


