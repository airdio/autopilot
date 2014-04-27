#! /usr/bin python

from autopilot.workflows.tasks.deployrole import DeployRole
from autopilot.common.utils import Dct
from autopilot.common.apenv import ApEnv

class TaskFactory(object):
    """
    Create task based on properties and environment data
    """
    @staticmethod
    def create(apenv, wf_id, inf, task_name, properties):
        wfInstance = apenv.get(wf_id)
        resolver = Dct.get(wfInstance, "resolver", TaskFactory)
        k = getattr(resolver, "create_{0}".format(task_name))
        return k(apenv, inf, wf_id, properties)

    @staticmethod
    def _create_deploy_role(apenv, inf, wf_id, props):
        return DeployRole(apenv, inf, wf_id, props)