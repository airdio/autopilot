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

    def serialize(self):
        return dict(name=self.name,
                    properties=dict(role_group=self.properties["role_group"].serialize()))

    def on_run(self, callback):
        """
        """
        # check what we have materilized in the workflow state (this is the stack state)
        materialized_spec = self.workflow_state.get("stack_spec").get("materialized")
        # todo: Handle the case when domains and stacks are not materialized. Throw exception

        mdomain_spec = materialized_spec.get("domain")
        mstack_spec = materialized_spec.get("stack")
        mrole_groups = materialized_spec.get("role_groups")

        #todo: Handle upgrade, scale out and scale back case

        # get the target role groups and roles from the properties
        target_role_group = self.properties.get("role_group")
        target_role_group_name = target_role_group.name

        # check if we have materialized instances already created for this role_group
        # if we don't then create instances first.
        if not mrole_groups or not mrole_groups.get(target_role_group_name):
            uname = "{0}.{1}.{2}".format(self.properties.get('stack'), target_role_group_name,
                                         materialized_spec.get("domain"))
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
                rc_instances = self.inf.provision_instances(domain_spec=mdomain_spec, stack_spec=mstack_spec,
                                                            instance_spec=instance_spec)

                # update materialized role groups
                if not mrole_groups:
                    mrole_groups = {}
                    materialized_spec.update(dict(role_groups=mrole_groups))
                mrole_groups[target_role_group_name] = rc_instances.spec

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


class DomainInit(Task):
    """
    Initialize a domain
    """
    Name = "DomainInit"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, DomainInit.Name, wf_id, inf, properties, workflow_state)

    def serialize(self):
        return dict(name=self.name, properties=dict(domain=self.properties.get("stack_spec").domain))

    def on_run(self, callback):
        # init domain only if we do not have a materiazlied domain
        if not self.workflow_state.get("stack_spec").get("materialized"):
            domain_spec = dict(domain=self.properties.get("stack_spec").domain)
            rc = self.inf.init_domain(domain_spec=domain_spec)
            self.workflow_state["stack_spec"].update(dict(materialized=dict(domain=rc.spec)))

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

    def serialize(self):
        return dict(name=self.name,  properties=dict(stack=self.properties.get("stack_spec").name))

    def on_run(self, callback):
        """
        Initialize stack
        """
        materialized_spec = self.workflow_state.get("stack_spec").get("materialized")
        if not materialized_spec:
            # todo: throw exception here since we do not have a domain
            pass
        if not self.workflow_state.get("stack_spec").get("materialized").get("stack"):
            # create a new stack since we do not have one
            domain_spec = materialized_spec.get("domain")
            rc = self.inf.init_stack(domain_spec=domain_spec, stack_spec={})

            # update workflow state with updated spec
            materialized_spec.update(dict(stack=rc.spec))

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def on_rollback(self, callback):
        """
        Delete domain
        """
        pass
