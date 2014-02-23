#! /usr/bin python

from autopilot.workflows.tasks.deploy_role import Deploy_Role
from autopilot.common.utils import Dct
from autopilot.common.apenv import ApEnv

class TaskFactory(object):
    """
    Create task based on properties and environment data
    """
    @staticmethod
    def create(wf_id, cloud, task_name, parent_workflow, properties):
        wfInstance = ApEnv.get(wf_id)
        resolver = Dct.get(wfInstance, TaskFactory)
        k = getattr(resolver, "_create_{0}".format(task_name))
        return k(cloud, parent_workflow, properties)

    @staticmethod
    def _create_deploy_role(cloud, parent_workflow, props):
        return Deploy_Role(cloud, parent_workflow, props)