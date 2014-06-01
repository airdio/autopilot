#! /usr/bin/python
import simplejson
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.workflows.tasks.taskfactory import TaskFactory
from autopilot.inf.infactory import InFactory
from autopilot.workflows.workflowexecutor import WorkflowExecutor


class WorkflowModel(object):
    """
    Object representation of a workflow
    """
    def __init__(self, apenv, wf_id, type, target, token, audit, inf, groupset):
        self.apenv = apenv
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.account = token
        self.audit = audit
        self.inf = inf
        self.groupset = groupset
        self.parallel = True
        self.executor = WorkflowExecutor(self)

    def get_executor(self):
        return self.executor

    @staticmethod
    def loads(apenv, model_str):
        modeld = simplejson.loads(model_str)
        inf = WorkflowModel._resolve_inf(Dct.get(modeld, "inf"))
        wf_id = Dct.get(modeld, "wf_id")
        return WorkflowModel(apenv,
                             wf_id,
                             Dct.get(modeld, "type"),
                             Dct.get(modeld, "target"),
                             Dct.get(modeld, "token"),
                             Dct.get(modeld, "audit"),
                             inf,
                             WorkflowModel._resolve_groupset(wf_id, apenv, inf, Dct.get(modeld, "taskgroups")))


    @staticmethod
    def _resolve_inf(inf_dict):
        """
        resolve infrastructure instance
        """
        target = Dct.get(inf_dict, "target")
        props = Dct.get(inf_dict, "properties")
        #todo: get aws access keys from the environment
        return InFactory.create(target, props)

    @staticmethod
    def _resolve_grouupset(wf_id, apenv, inf, tasksetd):
        groups = []
        for groupd in tasksetd:
            groups.append(WorkflowModel._resolve_group(wf_id, apenv, inf, groupd))
        return GroupSet(groups)

    @staticmethod
    def _resolve_group(wf_id, apenv, inf, groupd):
        groupid = Dct.get(groupd, "groupid")
        tasksd = Dct.get(groupd, "tasks")
        tasks = []
        for taskd in tasksd:
            tasks.append(TaskFactory.create(apenv, wf_id, inf, Dct.get(taskd, "name"),
                         Dct.get(taskd, "properties")))
        return Group(wf_id, apenv, groupid, tasks)



