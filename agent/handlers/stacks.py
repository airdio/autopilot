#! /usr/bin/python

from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.agent.tasks.InstallRole import InstallRole
from autopilot.protocol.message import Message


class Handler(object):
    """
    Entry point into handling incoming requests.
    """
    def __init__(self, apenv, message, callback=None):
        self.apenv = apenv
        self.type = message.type
        self.headers = message.headers
        self.data = message.data
        self.message = message
        self.callback = callback

    def process(self):
        pass


class StackDeployHandler(Handler):
    """
    Handle stack install
    """
    def __init__(self, apenv, message, callback=None):
        Handler.__init__(self, apenv, message, callback=callback)
        self.response = Message(type="stack_deploy_response", headers={}, data=None)

    def process(self, wait_event=None):
        """
        Process the stack deployment message

        :type: callable
        :param Any callable. Will be called when process completes

        :type: gevent.event.Event
        :param The :class:`gevent.event.Event` which will get signalled when the workflow completes. Test hook
        """
        stack = self.data.get("stack")
        role_group = self.data.get("target_role_group")

        if not stack.groups.get(role_group):
            #raise exception.InvalidTargetRoleGroup(role_group)
            pass

        wf_id = WorkflowModel.get_next_workflow_id(self.headers.get("domain"), "StackHandler")
        initial_workflow_state = {}
        tasks = []
        for role in stack.groups.get(role_group).roles:
            properties = {
                "stack": stack,
                "target_role_group": role_group,
                "target_role": role,
                "install_dirs": {
                    "root_dir": self.apenv.get("root_dir"),
                    "current_file": self.apenv.get("current_file"),
                    "versions_dir": self.apenv.get("versions_dir")
                }
            }
            tasks.append(InstallRole(apenv=self.apenv, wf_id=wf_id, inf=None,
                                     properties=properties, workflow_state=initial_workflow_state))

        model = WorkflowModel(wf_id=wf_id,
                              type="stack",
                              target=role_group,
                              inf=None,
                              domain=self.headers.get("domain"),
                              groupset=GroupSet([Group(wf_id=wf_id, apenv=self.apenv, groupid="install_agent_roles", tasks=tasks)]),
                              workflow_state=initial_workflow_state)

        ex = WorkflowExecutor(apenv=self.apenv, model=model)
        ex.execute(callback=self._executor_callback, wait_event=wait_event)

    def _executor_callback(self, executor):
        pass

