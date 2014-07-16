#! /usr/bin/python
import uuid
from autopilot.common import utils
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.workflows.tasks.task import Task, TaskState


class StackMapper(object):
    """
    Mapper class that merges role spec, stack spec and stack state into a workflow spec
    """
    def __init__(self, apenv, wf_id, org, domain, owner, stack_spec, roles_spec=[], stack_state={}):
        self.apenv = apenv
        self.wf_id = wf_id
        self.type = 'stack.deploy'
        self.target = self.stack_spec.name
        self.timestamp = utils.get_utc_now_seconds()
        self.owner = owner
        self.org = org
        self.domain = domain
        self.stack_spec = stack_spec
        self.roles_spec = roles_spec
        self.stack_state = stack_state
        self.inf = self._resolve_inf()
        self.taskgroups = self._build_task_groups()
        self._build_workflow()

    def _build_workflow(self):
        pass

    def _get_unique_wf_id(self):
        return uuid.uuid4()

    def _resolve_inf(self):
        properties = dict(properties=dict(aws_access_key_id=self.apenv.get('aws_access_key_id'),
                                          aws_secret_access_key=self.apenv.get('aws_access_key_id')))

        return self.apenv.get_inf_resolver(self.wf_id).resolve(apenv=self.apenv,
                                                               target=self.stack_spec.get('infrastructure'),
                                                               properties=properties)

    def _build_task_groups(self):
        groups = []
        #domain init task group
        domain_init_task = Task(apenv=self.apenv,
                                name="DomainInit",
                                wf_id=self.wf_id,
                                inf=self.inf,
                                properties=dict(proeprties=dict(domain=self.domain)),
                                workflow_state=self.stack_state)

        groups.append(Group(wf_id=self.wf_id, apenv=self.apenv, groupid="domain_init", tasks=[domain_init_task]))
        return GroupSet(groups)
