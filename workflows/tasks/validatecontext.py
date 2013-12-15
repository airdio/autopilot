__author__ = 'sujeet'

from autopilot.workflows.tasks.task import Task


class ValidateContext(Task):
    """ Validates the deployment context
     eg: like validate connectivity to cloud, privileges, network etc.
    """
    def __init__(self, name, deployment_context):
        Task.__init__(self, name)
        self.name = name
        self.context = deployment_context

    def run(self):
        pass

    def rollback(self):
        pass

