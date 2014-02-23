#! /usr/bin python
import simplejson
from autopilot.common.utils import Dct
from autopilot.workflows.tasks.taskfactory import TaskFactory
from autopilot.cloud.cloudfactory import CloudFactory
from autopilot.workflows.executor import WorkflowExecutor

class WorkflowModel(object):
    """ Define a workflow mode
    """
    def __init__(self, wf_id, type, target, token, audit, cloud, taskset):
        self.wf_id = wf_id
        self.type = type
        self.target = target
        self.account = token
        self.audit = audit
        self.cloud = cloud
        self.taskset = taskset
        self.parallel = True

    def run(self):
        wfe = WorkflowExecutor(self)
        wfe.execute()

    @staticmethod
    def loads(model_str):
        dct = simplejson.loads(model_str)
        cloud = Dct.get(dct, "cloud", True)
        return WorkflowModel(Dct.get(dct, "wf_id", True),
                             Dct.get(dct, "type", True),
                             Dct.get(dct, "target", True),
                             Dct.get(dct, "token", True),
                             Dct.get(dct, "audit", True),
                             WorkflowModel._get_cloud(cloud),
                             WorkflowModel._get_tasks(cloud, Dct.get(dct, "taskset", True)))

    @staticmethod
    def _get_cloud(cloud_dict):
        """
        resolve cloud instance
        """
        target = Dct.get(cloud_dict, "target", True)
        props = Dct.get(cloud_dict, "properties", True)
        #todo: get aws access keys from the environment
        return CloudFactory.create(target, props)

    """
    Resolves task instances
    """
    @staticmethod
    def _get_tasks(cloud, tasksetd):
        tasks = []
        for taskd in tasksetd:
            tasks.append(TaskFactory.create(cloud, Dct.get(taskd, "task", True),
                         Dct.get(taskd, "properties")))
        return tasks


