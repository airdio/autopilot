#! /usr/bin/python
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import Task, TaskResult, TaskState


class AWSDeployRole(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "AWSDeployRole"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, AWSDeployRole.Name, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        """
        """
        domain_spec = self.workflow_state["domain"]["spec"]
        stack_spec = self.workflow_state["stack"]["spec"]

        role_spec = {}
        rolename = self.properties["role"]
        auth_spec = []
        for port in self.properties["network"]["ports"]:
            auth_spec.append({"protocol": "tcp", "from": port, "to": port})

        role_spec["auth_spec"] = auth_spec
        role_spec["associate_public_ip"] = self.properties["network"]["public_ip"]
        role_spec["uname"] = rolename
        role_spec["instance_count"] = self.properties["instance_count"]
        role_spec["instance_type"] = self.properties["instance_type"]
        role_spec["image_id"] = self.properties["image_id"]
        role_spec["key_pair_name"] = self.properties["key_pair_name"]
        rc_role = self.inf.provision_role(domain_spec=domain_spec, stack_spec=stack_spec, role_spec=role_spec)

        self.workflow_state["roles"] = {}
        self.workflow_state["roles"][rolename] = {}
        self.workflow_state["roles"][rolename]["spec"] = rc_role.spec
        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        De-provision or rollback to a previous version
        """
        pass


class AWSDomainInit(Task):
    """
    Initialize a domain
    """
    Name = "AWSDomainInit"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, AWSDomainInit.Name, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        domain = self.properties.get("domain")
        rc = self.inf.init_domain(domain_spec={"domain": domain})
        self.workflow_state["domain"]["spec"] = rc.spec

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        Delete domain
        """
        pass

class AWSStackInit(Task):
    """
    Initialize a domain
    """
    Name = "AWSStackInit"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, AWSStackInit.Name, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        """
        """
        domain_spec = self.workflow_state["domain"]["spec"]
        stack_spec = {}
        rc_stack = self.inf.init_stack(domain_spec=domain_spec, stack_spec=stack_spec)
        self.workflow_state["stack"]["spec"] = rc_stack.spec

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        Delete domain
        """
        pass
