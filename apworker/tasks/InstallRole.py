#! /usr/bin/python

from autopilot.workflows.tasks.task import Task, TaskState
from autopilot.apworker.installers.InstallProviders import GitInstallProvider


class InstallRole(Task):
    """
    Install the role on this machine
    """
    Name = "InstallRole"

    def __init__(self, apenv, wf_id, inf, properties, workflow_state):
        Task.__init__(self, apenv, InstallRole.Name, wf_id, inf, properties, workflow_state)
        self.apenv = apenv
        self.target_role_group = properties.get('target_role_group')
        self.stack_spec = properties.get('stack_spec')
        self.materialized_roles = properties.get('materialized_roles')

    def on_run(self, callback):
        # check if the versions we have and the one being deployed are the same
        # If yes we just return
        for role in self.stack_spec.groups.get(self.target_role_group).roles:
            installed_version = self._get_installed_role_version()
            if installed_version == role.version:
                # we don;t need to do anything
                callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

            # either we are updating or we are installing this role for the first time
            self._install_role(role)

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def _get_installed_role_version(self, role):
        pass

    def _install_role(self, role):
        if role.deploy.get('git'):
            working_dir = '/tmp/{0}/{1}/{2}/{3}'.format(self.stack_spec.name, self.target_role_group, role.name,
                                                        role.version)
            installer = GitInstallProvider(self.apenv, role, self.target_role_group,
                                           self.stack_spec.name, working_dir)
            return installer.run()


    def _update_current_role_config(self, role):
        pass


