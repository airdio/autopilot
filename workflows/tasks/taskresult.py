#! /usr/bin python


class TaskState(object):
    """
    """
    Initialized = 0
    Started = 2
    Error = 4
    Done = 8


class TaskResult(object):
    """ Wraps the result of a task
    """
    def __init__(self, task, wf_id, state):
        self.tracked_task = task
        self.workflow = wf_id
        self.state = state
        self.notification_targets = []
        self.state_change_stack = [self.state]

    def update(self, message, new_state):
        if self.task_state != new_state:
            self.state = new_state
            self.state_change_stack.append(new_state)