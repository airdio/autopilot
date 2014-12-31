#! /usr/bin/python

from autopilot.common import utils
from autopilot.common.asyncpool import taskpool
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.tasks.group import Group, GroupSet
from autopilot.agent.tasks.InstallRoleTask import InstallRoleTask
from autopilot.protocol.message import Message
from autopilot.common import logger


class Handler(object):
    """
    Entry point into handling incoming requests.
    """
    def __init__(self, apenv, message_type):
        self.apenv = apenv
        self.message_type = message_type

    def process(self, message):
        pass


class StackDeployHandler(Handler):
    """
    Handle stack install message from the client
    Create a workflow with deploy role tasks
    """
    def __init__(self, apenv, message_type):
        Handler.__init__(self, apenv, message_type)
        self.log = logger.get_logger("StackDeployHandler")
        self.response = Message(type="stack_deploy_response", headers={}, data=None)

    def process(self, message):
        """
        Process the stack deployment message
        :type: callable
        :param Any callable. Will be called when process completes
        """
        process_future = taskpool.callable_future()

        # get the headers and data
        headers = message.headers
        data = message.data
        stack = data.get("stack")
        target_role_group = data.get("target_role_group")

        self.log.info("Processing message of type: {0}. Domain: {1}".format(self.message_type, headers.get("domain")))

        # build a workflow
        # for each role in the role group create a new task
        # each task should have a separate temporary working directory
        wf_id = WorkflowModel.get_next_workflow_id(headers.get("domain"), "StackHandler")
        initial_workflow_state = {target_role_group: {}, "wf_id": wf_id}
        tasks = []
        for role in stack.groups.get(target_role_group).roles:
            role_working_dir = utils.path_join(self.apenv.get("WORKING_DIR"), stack.name, wf_id, role)
            role_status_dir = utils.path_join(self.apenv.get("STATUS_DIR"), stack.name, role)
            utils.rmtree(role_working_dir)
            utils.mkdir(role_working_dir)
            utils.mkdir(role_status_dir)
            properties = {
                "stack": stack,
                "target_role_group": target_role_group,
                "target_role": role,
                "role_working_dir": role_working_dir,
                "role_status_dir": role_status_dir
            }
            initial_workflow_state[target_role_group][role] = {}

            tasks.append(InstallRoleTask(apenv=self.apenv, wf_id=wf_id, inf=None,
                                         properties=properties,
                                         workflow_state=initial_workflow_state))

        self.log.info("Executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                      .format(self.message_type, headers.get("domain"), wf_id))

        model = WorkflowModel(wf_id=wf_id,
                              type="stack",
                              target=target_role_group,
                              inf=None,
                              domain=headers.get("domain"),
                              groupset=GroupSet([Group(wf_id=wf_id, apenv=self.apenv,
                                                       groupid="install_agent_roles", tasks=tasks)]),
                              workflow_state=initial_workflow_state)

        def executor_callback(executor_future):
            rm = None
            executor = executor_future.value
            if executor.success:
                self.log.info("Success executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                              .format(self.message_type, headers.get("domain"), wf_id))

                rm = Message(type="response-stack-deploy",
                             headers={"domain": "dev.contoso.org"},
                             data=executor.model.workflow_state)
                process_future(result=rm, exception=None)
            else:
                self.log.error("Error executing workflow for message of type: {0}. Domain: {1}. Workflow Id: {2}"
                               .format(self.message_type, headers.get("domain"), wf_id))
                # todo: get exception data from the executor
                process_future(result=rm, exception=Exception())

        WorkflowExecutor(apenv=self.apenv, model=model).execute().on_complete(executor_callback)
        return process_future