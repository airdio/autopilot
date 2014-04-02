#! /usr/bin python
from autopilot.workflows.tasks.task import Task, TaskResult, TaskState


class DeployRole(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "Deploy Role"

    def __init__(self, cloud, props):
        Task(DeployRole.Name, cloud, props)
        self.result = TaskResult(self, TaskState.Initialized)

    def run(self, callback):
        self.result.state = TaskState.Done

    def rollback(self):
        """
        De-provision or rollback to a previous version
        """
        pass

