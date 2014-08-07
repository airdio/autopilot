#! /usr/bin/python
import os
from autopilot.common import utils


class GitInstallProvider(object):
    """
    Git install provider
    """
    def __init__(self, apenv, role, role_group_name, stack_name, working_dir):
        self.apenv = apenv
        self.role = role
        self.working_dir = working_dir
        self.stack_name = stack_name
        self.role_group_name = role_group_name

    def run(self):
        git_url = self.role.deploy.get('git')
        branch = self.role.deploy.get('branch')
        git_command = "git clone {0} {1} -b {2}".format(git_url, self.working_dir, branch)
        (retcode, out, error) = utils.subprocess_cmd(git_command)
        if retcode:
            raise Exception("git clone failed to fetch: {0} \n Error: {1}".format(git_command, error))

        #todo: check return code here
        runmod = self._load_run_module(self.working_dir)
        env = self._build_env()
        return runmod.install(env)

    def _load_run_module(self, path):
        import imp
        temp_module_name = '{0}.{1}.{2}.{3}'.format(self.stack_name, self.role_group_name,
                                                    self.role.name, self.role.version)
        return imp.load_source(temp_module_name, os.path.join(path, self.role.deploy.get('script')))

    def _build_env(self):
        return dict(target=self.role.name, stack=self.apenv.get("stack"))