#! /usr/bin python
import simplejson
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.task import TaskSet
from autopilot.workflows.tasks.taskfactory import TaskFactory
from autopilot.cloud.cloudfactory import CloudFactory
from autopilot.workflows.executor import WorkflowExecutor

class WorkflowModel(object):
    """ Define a workflow mode
    """
    def __init__(self, apenv, wf_id, type, target, token, audit, cloud, taskset):
        self.apenv = apenv
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.account = token
        self.audit = audit
        self.cloud = cloud
        self.taskset = taskset
        self.parallel = True

    def get_executor(self):
        return WorkflowExecutor(self)

    @staticmethod
    def loads(apenv, model_str):
        dct = simplejson.loads(model_str)
        cloud = Dct.get(dct, "cloud")
        wf_id = Dct.get(dct, "wf_id")
        return WorkflowModel(apenv,
                             wf_id,
                             Dct.get(dct, "type"),
                             Dct.get(dct, "target"),
                             Dct.get(dct, "token"),
                             Dct.get(dct, "audit"),
                             WorkflowModel._get_cloud(cloud),
                             WorkflowModel._get_tasks(wf_id, apenv, cloud, Dct.get(dct, "taskset")))

    @staticmethod
    def _get_cloud(cloud_dict):
        """
        resolve cloud instance
        """
        target = Dct.get(cloud_dict, "target")
        props = Dct.get(cloud_dict, "properties")
        #todo: get aws access keys from the environment
        return CloudFactory.create(target, props)

    """
    Resolves task instances
    """
    @staticmethod
    def _get_tasks(wf_id, apenv, cloud, tasksetd):
        taskset = TaskSet(Dct.get(tasksetd, "parallel"))
        tasksd = Dct.get(tasksetd, "tasks", [])
        for taskd in tasksd:
            taskset.tasks.append(TaskFactory.create(apenv, wf_id, cloud, Dct.get(taskd, "name"),
                         Dct.get(taskd, "properties")))
        return taskset


