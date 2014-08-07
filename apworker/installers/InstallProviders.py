#! /usr/bin/python
import os
from autopilot.common import utils
from autopilot.common import exception


class GitInstallProvider(object):
    """
    Git install provider
    """
    def __init__(self, apenv, role, role_group_name, stack_name, working_dir):
        self.apenv = apenv
        self.role = role
        self.clone_dir = working_dir
        self.stack_name = stack_name
        self.role_group_name = role_group_name

    def run(self):
        git_url = self.role.deploy.get('git')
        branch = self.role.deploy.get('branch')
        self._ensure_clean_working_dir()
        git_command = "git clone {0} {1} -b {2}".format(git_url, self.clone_dir, branch)
        (return_code, out, error) = utils.subprocess_cmd(git_command)
        if return_code:
            raise exception.GitInstallProviderException("git clone failed to fetch: {0} \n Error: {1}"
                                                        .format(git_command, error))
        try:
            #todo: check return code here
            runmod = self._load_run_module(self.clone_dir)
            env = self._build_env()
            return runmod.install(env)
        except Exception as ex:
            raise exception.GitInstallProviderException("Error", inner_exception=ex)

    def _ensure_clean_working_dir(self):
        utils.rmtree(self.clone_dir)
        utils.mkdir(self.clone_dir)

    def _load_run_module(self, path):
        import imp
        temp_module_name = '{0}.{1}.{2}.{3}'.format(self.stack_name, self.role_group_name,
                                                    self.role.name, self.role.version)
        return imp.load_source(temp_module_name, os.path.join(path, self.role.deploy.get('script')))

    def _build_env(self):
        return dict(target=self.role.name, stack=self.apenv.get("stack"),
                    working_dir=self.clone_dir)