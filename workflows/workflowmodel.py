#! /usr/bin/python
import simplejson
from autopilot.workflows.tasks.group import Group, GroupSet


class WorkflowModel(object):
    """
    Object representation of a workflow
    """
    def __init__(self, wf_id, type, target, domain, inf, groupset, workflow_state={}):
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.inf = inf
        self.domain = domain
        self.groupset = groupset
        self.workflow_state = workflow_state

    def serialize(self):
        return dict(wf_id=self.wf_id,
                    type=self.type,
                    target=self.target,
                    inf=self.inf.serialize(),
                    domain=self.domain,
                    groupset=self.groupset.serialize())

    @staticmethod
    def load(apenv, wf_spec_stream, workflow_state={}):
        """
        Loads a serialized workflow model
        """
        modeld = simplejson.load(wf_spec_stream)
        wf_id = modeld.get("wf_id")
        type = modeld.get("type")
        target = modeld.get("target")
        domain = modeld.get("domain")
        infd = modeld.get('inf')
        inf = apenv.get_inf_resolver(wf_id).resolve(apenv=apenv, target=infd.get('target'), properties=infd.get('properties'))
        groupset = WorkflowModel._resolve_groupset(apenv=apenv, wf_id=wf_id, inf=inf,
                                                   workflow_state=workflow_state, groupsetd=modeld.get('taskgroups'))

        return WorkflowModel(wf_id=wf_id,
                             type=type,
                             target=target,
                             inf=inf,
                             domain=domain,
                             groupset=groupset,
                             workflow_state=workflow_state)

    @staticmethod
    def _resolve_groupset(apenv, wf_id, inf, workflow_state, groupsetd):
        """
        Resolve groups and tasks
        """
        groups = []
        for groupd in groupsetd:
            groups.append(WorkflowModel._resolve_group(apenv=apenv, wf_id=wf_id, inf=inf,
                                                       workflow_state=workflow_state, groupd=groupd))
        return GroupSet(groups)

    @staticmethod
    def _resolve_group(apenv, wf_id, inf, workflow_state, groupd):
        """
        Resolve tasks within a group
        """
        groupid = groupd.get("groupid")
        tasksd = groupd.get("tasks")
        tasks = []
        task_resolver = apenv.get_task_resolver(wf_id)
        for taskd in tasksd:
            tasks.append(task_resolver.resolve(taskd.get("name"), apenv, wf_id,
                                               inf, taskd.get("properties"), workflow_state))
        return Group(wf_id, apenv, groupid, tasks)