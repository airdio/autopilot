#! /usr/bin python
from autopilot.workflows.tasks.task import Task
from autopilot.workflows.tasks.taskresult import TaskResult, TaskState


class Deploy_Role(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "deploy_role"

    def __init__(self, cloud, props):
        Task(Deploy_Role.Name, cloud, props)

    def run(self, callback):
        self.task_result = TaskResult(self, TaskState.Initialized)

    def rollback(self):
        """
        De-provision or rollback to a previous version
        """
        pass


