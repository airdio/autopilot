#! /usr/bin/python
from autopilot.workflows.tasks.task import Task, TaskResult, TaskState


class DeployRole(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "Deploy Role"

    def __init__(self, apenv, wf_id, inf, properties):
        Task.__init__(self, apenv, DeployRole.Name, wf_id, inf, properties)

    def run(self, callback):
        self.result.state = TaskState.Done

    def rollback(self):
        """
        De-provision or rollback to a previous version
        """
        pass


class DomainInit(Task):
    """
    Initialize a domain
    """
    Name = "Domain Init"

    def __init__(self, apenv, wf_id, inf, properties):
        Task.__init__(self, apenv, DomainInit.Name, wf_id, inf, properties)

    def run(self, callback):
        self.inf.init_domain()

    def rollback(self):
        """
        De-provision or rollback to a previous version
        """
        pass

