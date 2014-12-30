#! /usr/bin/python

from autopilot.common import logger
from autopilot.common import utils
from autopilot.common.exception import AutopilotException
from autopilot.workflows.tasks.task import Task, TaskState
from autopilot.agent.installers.InstallProviders import GitInstallProvider


class InstallRoleTask(Task):
    """
    Install the role on this machine
    This is called by the the ap agent running on a vm/container.
    """
    Name = "InstallRole"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, InstallRoleTask.Name, wf_id, inf, properties, workflow_state)
        self.log = logger.get_workflow_logger("InstallRoleTask")
        self.apenv = apenv
        self.stack = properties.get("stack")
        self.target_role_group = properties.get("target_role_group")
        self.target_role = properties.get("target_role")
        self.stack_name = self.stack.name
        self.role_groups = self.stack.groups

        self.working_dir = properties.get("working_dir")

    def on_run(self, callback):
        self.log.info("Installing target role {0} for role_group {1}"
                      .format(self.target_role, self.target_role_group), self.wf_id)

        try:
            self.log.info("Running GitInstaller for role: {0}. Working dir: {1}"
                          .format(self.target_role, self.working_dir), self.wf_id)

            GitInstallProvider(self.apenv, self.target_role, self.target_role_group,
                               self.stack, self.working_dir).run()

            self._update_current_version_file()

            callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

        except Exception as ex:
            self.log.error("InstallRole raised error", wf_id=self.wf_id, exc_info=ex)
            raise

    def _update_current_version_file(self):
        version_file_path = utils.path_join(self.working_dir, "autopilot",
                                            self.stack_name, "current")
        with open(version_file_path, 'w') as f:
            f.write(self.stack.name + '\n')
            f.write(self.target_role_group + '\n')
            f.write(self.target_role + '\n')