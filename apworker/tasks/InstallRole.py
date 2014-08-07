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
        if self._new_stack_install():
            # this is a new stack install
            self._bootstrap_stack_config()
            self._install_all_roles()
        else:
            # check if the versions we have and the one being deployed are the same
            # If yes we just return
            for role in self.stack_spec.groups.get(self.target_role_group).roles:
                if role.version != self._get_installed_role_config():
                    self._install_role(role)
                    self._update_current_role_config(role)

        callback(TaskState.Done, ["Task {0} done".format(self.name)], [])

    def _install_all_roles(self, role):
        for role in self.stack_spec.groups.get(self.target_role_group).roles:
            self._install_role(role)
            self._update_current_role_config(role)

    def _install_role(self, role):
        if role.deploy.get('git'):
            working_dir = '/tmp/{0}/{1}/{2}/{3}'.format(self.stack_spec.name, self.target_role_group, role.name,
                                                        role.version)
            installer = GitInstallProvider(self.apenv, role, self.target_role_group,
                                           self.stack_spec.name, working_dir)
            return installer.run()


    def _update_current_role_config(self, role):
        pass