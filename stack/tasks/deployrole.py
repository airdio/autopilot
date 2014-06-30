#! /usr/bin/python
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import Task, TaskResult, TaskState


class DeployRole(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "DeployRole"

    def __init__(self, apenv, wf_id, inf, properties):
        Task.__init__(self, apenv, DeployRole.Name, wf_id, inf, properties)

    def on_run(self, callback):
        self.result.state = TaskState.Done

    def on_rollback(self, callback):
        """
        De-provision or rollback to a previous version
        """
        pass


class DomainInit(Task):
    """
    Initialize a domain
    """
    Name = "DomainInit"

    def __init__(self, apenv, wf_id, inf, properties):
        Task.__init__(self, apenv, DomainInit.Name, wf_id, inf, properties)

    def on_run(self, callback):
        domain = Dct.get(self.properties, "domain")
        rc = self.inf.init_domain(domain_spec={"domain": domain})
        domain_spec = rc.spec

    def on_rollback(self, callback):
        """
        Delete domain
        """
        pass
