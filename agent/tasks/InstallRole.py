#! /usr/bin/python

from autopilot.common.logger import wflog
from autopilot.common import utils
from autopilot.workflows.tasks.task import Task, TaskState
from autopilot.agent.installers.InstallProviders import GitInstallProvider


class InstallRole(Task):
    """
    Install the role on this machine
    """
    Name = "Autopilot.Agent.InstallRole"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, InstallRole.Name, wf_id, inf, properties, workflow_state)
        self.apenv = apenv
        self.target_role_group = properties.get("target")
        self.stack = properties.get("stack")
        self.stack_name = self.stack.name
        self.role_groups = self.stack.groups

        self.root_dir = properties.get("install_dirs").get("root_dir")
        self.current_file = properties.get("install_dirs").get("current_file")
        self.versions_dir = properties.get("install_dirs").get("versions_dir")

    def on_run(self, callback):
        # check if the versions we have and the one being deployed are the same
        # If yes we just return
        for role in self.role_groups.get(self.target_role_group).roles:
            installed_version = self._get_installed_role_version(role)
            wflog.info("For role {0} Installed role version is {1} and target version is role {2}"
                       .format(role.name, installed_version, role.version), self.wf_id)

            if installed_version and installed_version == str(role.version):
                # we don't need to do anything
                wflog.info("Installed version is same as target version. Skipping", self.wf_id)
                callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

            # either we are updating to another version or we are installing this role for the first time
            working_dir = utils.path_join(self.root_dir, self.stack_name, self.target_role_group,
                                          role.name, self.versions_dir, str(role.version))
            self._install_role(working_dir, role)

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def _get_installed_role_version(self, role):
        current_file_path = utils.path_join(self.root_dir, self.stack_name,
                                            self.target_role_group, role.name, self.current_file)
        if utils.path_exists(current_file_path):
            with open(current_file_path, 'r') as f:
                return f.readline()
        return None

    def _install_role(self, working_dir, role):
        installer = None
        # ensure we have an existing working dir
        utils.mkdir(working_dir)
        if role.deploy.get('git'):
            wflog.info("Running GitInstaller for role: {0}. Working dir: {1}".format(role.name, working_dir),
                       self.wf_id)
            installer = GitInstallProvider(self.apenv, role, self.target_role_group, self.stack, working_dir)
        if installer:
            return installer.run()
        else:
            wflog.warning("No installer found to install role: {0}. Working dir: {1}".format(role.name, working_dir),
                          self.wf_id)

    def _update_current_role_config(self, role):
        current_file_path = utils.path_join(self.root_dir, self.stack_name,
                                            self.target_role_group, role.name, self.current_file)
        with open(current_file_path, 'w') as f:
            f.write(role.version)