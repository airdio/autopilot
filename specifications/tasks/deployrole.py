#! /usr/bin/python
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import Task, TaskResult, TaskState


class DeployRole(Task):
    """
    Provisions a role to 1 or more instances
    Always runs as part of a workflow
    """
    Name = "DeployRole"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, DeployRole.Name, wf_id, inf, properties, workflow_state)

    def on_run(self, callback):
        """
        """
        # check what we have in the workflow state (this is the stack state)
        domain_spec = self.workflow_state["domain"]["spec"]
        stack_spec = self.workflow_state["stack"]["spec"]
        role_groups = self.workflow_state["role_groups"]

        # get role and role group from the properties
        role_group_name = self.properties.get("role_group")
        rolename = self.properties.get("role")
        uname = "{0}.{1}.{2}".format(self.properties.get('stack'), role_group_name,
                                     self.properties.get('domain'))

        #check if we have a instances already created for this role_group
        # if we don't then create instances first.
        existing_instances_spec = self._get_existing_instances_spec(role_groups, role_group_name)
        if not existing_instances_spec:
            # we don't have provisioned instances for this group
            # ...so provision instances
            auth_spec = []
            for port in self.properties["network"]["ports"]:
                auth_spec.append({"protocol": "tcp", "from": port, "to": port})
                instance_spec = {}
                instance_spec["uname"] = uname # unique name for this provision
                instance_spec["auth_spec"] = auth_spec
                instance_spec["associate_public_ip"] = self.properties["network"]["public_ip"]
                instance_spec["instance_count"] = self.properties["instance_count"]
                instance_spec["instance_type"] = self.properties["instance_type"]
                instance_spec["image_id"] = self.properties["image_id"]
                instance_spec["key_pair_name"] = self.properties["key_pair_name"]
                rc_instances = self.inf.provision_instances(domain_spec=domain_spec, stack_spec=stack_spec,
                                                            instance_spec=instance_spec)

                self.workflow_state["role_groups"][role_group_name] = {}
                self.workflow_state["role_groups"][role_group_name]["instances"] = rc_instances.spec['instances']
                self.workflow_state["role_groups"][role_group_name]["spec"] = rc_instances.spec

        # verify if agents are running on each instance
        self._verify_instance_agents()

        # call into the agents and deploy the role
        self._install_role()

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        De-provision or rollback to a previous version
        """
        pass

    def _verify_instance_agents(self, instances=[]):
        """
        Check if agents are installed on the instances
        """
        pass

    def _install_role(self):
        """
         1. Setup the environment parameters
            - Current role parameters
            - Stack parameters
         2. Wrap into a message
         3. Send it to the remote agent.
        """
        pass

    def _get_existing_instances_spec(self, role_groups, role_group_name):
        for (rg, val) in role_groups.items():
            if rg == role_group_name:
                return val['instances']
        return None


class DomainInit(Task):
    """
    Initialize a domain
    """
    Name = "DomainInit"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, DomainInit.Name, wf_id, inf, properties, workflow_state)

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

class StackInit(Task):
    """
    Initialize a domain
    """
    Name = "StackInit"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, StackInit.Name, wf_id, inf, properties, workflow_state)

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
