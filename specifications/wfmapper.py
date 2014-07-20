#! /usr/bin/python
import uuid
from autopilot.common import utils
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.workflows.tasks.task import Task
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.specifications.tasks.deployrole import DeployRole


class StackMapper(object):
    """
    Mapper class that merges role spec, stack spec and stack state into a workflow spec
    """
    def __init__(self, apenv, wf_id, org, domain, owner, stack_spec,
                 roles_spec, stack_state={}):
        self.type = 'stack'
        self.apenv = apenv
        self.wf_id = wf_id
        self.type = 'stack.deploy'
        self.timestamp = utils.get_utc_now_seconds()
        self.owner = owner
        self.org = org
        self.domain = domain
        self.stack_spec = stack_spec
        self.roles_spec = roles_spec
        self.stack_state = stack_state
        self.inf = self._resolve_inf()
        self.taskgroups = self._build_task_groups()

    def build_workflow(self):
        return WorkflowModel(wf_id=self.wf_id,
                             type=self.type,
                             target=self.stack_spec.name,
                             inf=self.inf,
                             domain=self.domain,
                             groupset=self.taskgroups,
                             workflow_state=self.stack_state)

    def _get_unique_wf_id(self):
        return uuid.uuid4()

    def _resolve_inf(self):
        # properties = dict(properties=dict(aws_access_key_id=self.apenv.get('aws_access_key_id'),
        #                                   aws_secret_access_key=self.apenv.get('aws_access_key_id')))

        target = self.stack_spec.inf
        properties = self.apenv.get('inf').get(target)
        return self.apenv.get_inf_resolver(self.wf_id).resolve(apenv=self.apenv,
                                                               target=target,
                                                               properties=properties)

    def _build_task_groups(self):
        """
        We always add domain init and stack init tasks to the groups even if
        they might not be needed (there is an existing domain and stack).
        We will let the inf implementation check if there is one and its
        healthy.
        """
        groups = []
        #domain init task group
        domain_init_task = Task(apenv=self.apenv,
                                name="DomainInit",
                                wf_id=self.wf_id,
                                inf=self.inf,
                                properties=dict(proeprties=dict(domain=self.domain)),
                                workflow_state=self.stack_state)

        groups.append(Group(wf_id=self.wf_id, apenv=self.apenv, groupid="domain_init", tasks=[domain_init_task]))

        #stack init
        stack_init_task = Task(apenv=self.apenv,
                               name="StackInit",
                               wf_id=self.wf_id,
                               inf=self.inf,
                               properties=dict(proeprties=dict(stack=self.stack_spec.name)),
                               workflow_state=self.stack_state)

        groups.append(Group(wf_id=self.wf_id, apenv=self.apenv, groupid="stack_init", tasks=[stack_init_task]))

        # Deploy roles
        # todo scale units(rolling upgrades). We need a canary role

        ordered_role_groups = []
        parallel_role_groups = []
        for (key, role_group) in self.stack_spec.groups.items():
            if role_group.order:
                ordered_role_groups.append(role_group)
            else:
                # we will add this to a group for parallel execution.
                parallel_role_groups.append(role_group)


        def _role_group_cmp(g1, g2):
            if g1.x == g2.x:
                return 0
            if g1.x < g2.x:
                return -1
            return 1

        # for ordered role groups we create a task group per role group
        # after they are sorted
        ordered_role_groups.sort(cmp=_role_group_cmp)
        for role_group in ordered_role_groups:
            properties = {}
            properties.update(dict(role_group=role_group))
            roles={}
            for roleref in role_group.rolerefs:
                roles[roleref] = self.roles_spec.roles.get(roleref)

            task = DeployRole(apenv=self.apenv, wf_id=self.wf_id, inf=self.inf,
                              properties=properties, workflow_state=self.stack_state)

            groups.append(Group(wf_id=self.wf_id, apenv=self.apenv,
                                groupid="ordered_deploy_roles_{0}".format(role_group.order),
                                tasks=[task]))

        # for parallel role groups we only need one task group
        parallel_tasks = []
        for role_group in parallel_role_groups:
            properties = {}
            properties.update(dict(role_group=role_group))
            roles={}
            for roleref in role_group.rolerefs:
                roles[roleref] = self.roles_spec.roles.get(roleref)

            task = DeployRole(apenv=self.apenv, wf_id=self.wf_id, inf=self.inf,
                              properties=properties, workflow_state=self.stack_state)
            parallel_tasks.append(task)
        groups.append(Group(wf_id=self.wf_id, apenv=self.apenv,
                            groupid="parallel_deploy_roles", tasks=parallel_tasks))

        return GroupSet(groups)