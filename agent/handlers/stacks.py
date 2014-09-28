#! /usr/bin/python

from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.agent.tasks.InstallRole import InstallRole
from autopilot.protocol.message import Message
from autopilot.common.logger import aglog
from autopilot.common import exception

class Handler(object):
    """
    Entry point into handling incoming requests.
    """
    def __init__(self, apenv, message_type):
        self.apenv = apenv
        self.message_type = message_type


    def process(self, message, callback=None):
        pass


class StackDeployHandler(Handler):
    """
    Handle stack install
    """
    def __init__(self, apenv, message_type):
        Handler.__init__(self, apenv, message_type)
        self.response = Message(type="stack_deploy_response", headers={}, data=None)

    def process(self, message, process_callback=None):
        """
        Process the stack deployment message

        :type: callable
        :param Any callable. Will be called when process completes
        """
        headers = message.headers
        data = message.data
        stack = data.get("stack")
        role_group = data.get("target_role_group")

        aglog.info("Processing message of type: {0}. Domain: {1}".format(self.message_type, headers.get("domain")))

        if not stack.groups.get(role_group):
            raise exception.InvalidTargetRoleGroup(role_group)
            pass

        wf_id = WorkflowModel.get_next_workflow_id(headers.get("domain"), "StackHandler")
        initial_workflow_state = {role_group: {}}
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
            initial_workflow_state[role_group][role.name] = {}
            tasks.append(InstallRole(apenv=self.apenv, wf_id=wf_id, inf=None,
                                     properties=properties, workflow_state=initial_workflow_state))

        aglog.info("Executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                   .format(self.message_type, headers.get("domain"), wf_id))

        model = WorkflowModel(wf_id=wf_id,
                              type="stack",
                              target=role_group,
                              inf=None,
                              domain=headers.get("domain"),
                              groupset=GroupSet([Group(wf_id=wf_id, apenv=self.apenv,
                                                       groupid="install_agent_roles", tasks=tasks)]),
                              workflow_state=initial_workflow_state)

        def executor_callback(executor):
            # paser execution state and create a response
            rm = None
            if executor.success:
                aglog.info("Success executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                           .format(self.message_type, headers.get("domain"), wf_id))

                rm = Message(type="response-stack-deploy",
                             headers={"domain": "dev.contoso.org"},
                             data=executor.model.workflow_state[role_group])
                process_callback(result=rm, exception=None)
            else:
                aglog.error("Error executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                            .format(self.message_type, headers.get("domain"), wf_id))
                # todo: get exception data from the executor
                process_callback(result=rm, exception=Exception())

        WorkflowExecutor(apenv=self.apenv, model=model).execute(callback=executor_callback)


