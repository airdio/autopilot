#! /usr/bin/python
import simplejson
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.group import TaskGroup
from autopilot.workflows.tasks.taskfactory import TaskFactory
from autopilot.cloud.cloudfactory import CloudFactory
from autopilot.workflows.workflowexecutor import WorkflowExecutor

class WorkflowModel(object):
    """
    Object representation of a workflow
    """
    def __init__(self, apenv, wf_id, type, target, token, audit, cloud, taskgroups):
        self.apenv = apenv
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.account = token
        self.audit = audit
        self.cloud = cloud
        self.taskgroups = taskgroups
        self.parallel = True
        self.executor = WorkflowExecutor(self)

    def get_executor(self):
        return self.executor

    @staticmethod
    def loads(apenv, model_str):
        modeld = simplejson.loads(model_str)
        cloud = WorkflowModel._resolve_cloud(Dct.get(modeld, "cloud"))
        wf_id = Dct.get(modeld, "wf_id")
        return WorkflowModel(apenv,
                             wf_id,
                             Dct.get(modeld, "type"),
                             Dct.get(modeld, "target"),
                             Dct.get(modeld, "token"),
                             Dct.get(modeld, "audit"),
                             cloud,
                             WorkflowModel._resolve_taskgroups(wf_id, apenv, cloud, Dct.get(modeld, "taskgroups")))


    @staticmethod
    def _resolve_cloud(cloud_dict):
        """
        resolve cloud instance
        """
        target = Dct.get(cloud_dict, "target")
        props = Dct.get(cloud_dict, "properties")
        #todo: get aws access keys from the environment
        return CloudFactory.create(target, props)

    @staticmethod
    def _resolve_taskgroups(wf_id, apenv, cloud, tasksetd):
        groups = []
        for groupd in tasksetd:
            groups.append(WorkflowModel._resolve_group(wf_id, apenv, cloud, groupd))
        return groups

    @staticmethod
    def _resolve_group(wf_id, apenv, cloud, groupd):
        groupid = Dct.get(groupd, "groupid")
        tasksd = Dct.get(groupd, "tasks")
        tasks = []
        for taskd in tasksd:
            tasks.append(TaskFactory.create(apenv, wf_id, cloud, Dct.get(taskd, "name"),
                         Dct.get(taskd, "properties")))
        return TaskGroup(wf_id, apenv, groupid, tasks)



