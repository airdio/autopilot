#! /usr/bin python

from autopilot.common.exception import AutopilotException


class TaskResolver(object):
    """
    Resolves tasks from task names
    """
    def __init__(self, container_class):
        self.container_class = container_class

    def resolve(self, task_name, apenv, wf_id, inf, properties, workflow_state):
        """
        Override this method to give custom implementations
        """
        func = getattr(self.container_class, "get_{0}".format(task_name))
        if callable(func):
            return func(apenv, inf, wf_id, properties, workflow_state)
        raise AutopilotException("Only callables are allowed")