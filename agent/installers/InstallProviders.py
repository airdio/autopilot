#! /usr/bin/python
import os
import json
from autopilot.common import utils
from autopilot.common import exception
from autopilot.common.logger import log


class InstallProvider(object):
    """
    InstallProvider Base class
    """
    def __init__(self, apenv, role, role_group_name, stack_spec, working_dir):
        self.apenv = apenv
        self.role = role
        self.working_dir = working_dir
        self.stack_spec = stack_spec
        self.role_group_name = role_group_name


class GitInstallProvider(InstallProvider):
    """
    Git install provider
    """
    LOG_SOURCE = "GitInstallProvider"
    def __init__(self, apenv, role, role_group_name, stack_spec, working_dir):
         InstallProvider.__init__(self, apenv, role, role_group_name, stack_spec, working_dir)

    def run(self, blocking=True, timeout=120):
        git_url = self.role.deploy.get('git')
        branch = self.role.deploy.get('branch')
        self._ensure_clean_working_dir()
        git_command = "git clone {0} {1} -b {2}".format(git_url, self.working_dir, branch)
        log.info(GitInstallProvider.LOG_SOURCE, "Cloning from git. Command: {0}".format(git_command))
        (return_code, out, error) = utils.subprocess_cmd(git_command, blocking=blocking)
        if return_code:
            log.error(GitInstallProvider.LOG_SOURCE, "Error cloning: Return Code: {0}. Error: {1}".format(return_code, error))
            raise exception.GitInstallProviderException("git clone failed: Command: {0} Return Code: {1} Error: {2}"
                                                        .format(git_command, return_code, error))

        (return_code, out, error) = self._install(blocking=blocking, timeout=timeout)
        if return_code:
            log.error(GitInstallProvider.LOG_SOURCE,
                      "Installation failed: Return Code: {0}. Error: {1}".format(return_code, error))
            raise exception.GitInstallProviderException("Installation failed. \n Error: {0}"
                                                        .format(error))

        log.info(GitInstallProvider.LOG_SOURCE, "Installation done. Output: {0}".format(out))

    def _ensure_clean_working_dir(self):
        utils.rmtree(self.working_dir)
        utils.mkdir(self.working_dir)

    def _build_env(self):
        d = dict(target=self.role.name, working_dir=self.working_dir)
        d.update(self.stack_spec.serialize())
        d.update(materialized=None)
        return json.dumps(d)

    def _install(self, blocking, timeout):
        script_file = self.role.deploy.get('script')
        module_name, extension = os.path.splitext(script_file)

        log.info(GitInstallProvider.LOG_SOURCE, "Installing module: {0}".format(script_file))
        if extension == ".py":
            return SafePythonModuleRunner().run(ap_env_json=self._build_env(),
                                                working_dir=self.working_dir,
                                                module_name=module_name,
                                                blocking=blocking, timeout=timeout)
        else:
            # assume some executable
            # todo: may not be safe
            return SafeShellModuleRunner().run(ap_env_json=self._build_env(),
                                               working_dir=self.working_dir,
                                               module_name=script_file,
                                               blocking=blocking, timeout=timeout)


class SafeShellModuleRunner(object):
    """
    Loads user provider shell script in a different process and runs
    desired actions
    """
    def run(self, ap_env_json, working_dir, module_name, blocking=True, timeout=None):
        env_tmp_file = os.path.join(working_dir, 'apenv.json')
        with open(env_tmp_file, 'w') as f:
            f.write(ap_env_json)
            f.write("\n")
        command = "./" + module_name
        return utils.subprocess_cmd(command, working_dir=working_dir, blocking=blocking)


class SafePythonModuleRunner(object):
    """
    Loads user provider python scripts in a different process and runs
    desired actions
    """
    def run(self, ap_env_json, working_dir, module_name, blocking=True, timeout=None):
        env_tmp_file = os.path.join(working_dir, 'apenv.json')
        with open(env_tmp_file, 'w') as f:
            f.write(ap_env_json)
        command = "python -c \"import test; import json; import os; env=json.load(open('{1}')); import {2}; {2}.install(env=env)\"".format(ap_env_json, env_tmp_file, module_name)
        return utils.subprocess_cmd(command, working_dir=working_dir, blocking=blocking)
