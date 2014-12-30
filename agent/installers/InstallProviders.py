#! /usr/bin/python
import os
import json
import yaml
from autopilot.common import utils
from autopilot.common import exception
from autopilot.common import logger


class InstallProvider(object):
    """
    InstallProvider Base class
    """
    def __init__(self, apenv, role, role_group_name, stack_spec, repo_base_dir):
        self.apenv = apenv
        self.role = role
        self.role_group_name = role_group_name
        self.stack_spec = stack_spec
        self.repo_base_dir = repo_base_dir


class GitInstallProvider(InstallProvider):
    """
    Git install provider
    """
    LOG_SOURCE = "GitInstallProvider"

    def __init__(self, apenv, role, role_group_name, stack_spec, repo_base_dir):
        InstallProvider.__init__(self, apenv, role, role_group_name, stack_spec, repo_base_dir)
        self.log = logger.get_logger("GitInstallProvider")

    def run(self, blocking=True, timeout=120):
        git_url = self.stack_spec.deploy.git
        branch = self.stack_spec.deploy.branch
        git_command = "git clone {0} {1} -b {2}".format(git_url, self.repo_base_dir, branch)
        self.log.info("Cloning from git. Command: {0}".format(git_command))
        (return_code, out, error) = utils.subprocess_cmd(git_command, blocking=blocking)
        if return_code:
            self.log.error("Error cloning: Return Code: {0}. Error: {1}".format(return_code, error))
            raise exception.GitInstallProviderException("git clone failed: Command: {0} Return Code: {1} Error: {2}"
                                                        .format(git_command, return_code, error))

        (return_code, out, error) = self._install(blocking=blocking, timeout=timeout)
        if return_code:
            self.log.error("Installation failed: Return Code: {0}. Error: {1}".format(return_code, error))
            raise exception.GitInstallProviderException("Installation failed. \n Error: {0}"
                                                        .format(error))

        self.log.info("Installation done. Output: {0}".format(out))

    def _build_env(self, role_dir):
        d = dict(target=self.role, working_dir=role_dir)
        d.update(self.stack_spec.serialize())
        d.update(materialized=None)
        return json.dumps(d)

    def _install(self, blocking, timeout):
        role_dir = utils.path_join(self.repo_base_dir, "autopilot", self.stack_spec.name, self.role)
        meta = self._read_metafile(role_dir, self.stack_spec.deploy.metafile)

        self.log.info("Role directory is {0}:".format(role_dir))
        if not utils.path_exists(role_dir):
            raise exception.GitInstallProviderException("Install directory path is malformed")

        if meta.get("deploy", "python") == "python":
            self.log.info("Installing python module setup.py")
            (module_name, extension) = os.path.splitext(meta.get("script", "setup.py"))
            return SafePythonModuleRunner().run(ap_env_json=self._build_env(role_dir=role_dir),
                                                working_dir=role_dir,
                                                module_name=module_name,
                                                blocking=blocking, timeout=timeout)
        else:
            # shell for now
            self.log.info("Installing from shell file setup.sh")
            return SafeShellModuleRunner().run(ap_env_json=self._build_env(role_dir=role_dir),
                                               working_dir=role_dir,
                                               module_name=meta.get("script", "setup.sh"),
                                               blocking=blocking, timeout=timeout)

    def _read_metafile(self, role_dir, metafile):
        metafile_path = utils.path_join(role_dir, metafile)
        if metafile.strip() and utils.path_exists(metafile_path):
            self.log.info("Reading metafile at: {0}".format(metafile_path))
            return yaml.load(open(metafile_path)).get("meta")
        else:
            return {}


class SafeShellModuleRunner(object):
    """
    Loads user provider shell script in a different process and runs
    desired actions
    """
    def __init__(self):
        self.log = logger.get_logger("SafeShellModuleRunner")

    # todo: use timeout
    def run(self, ap_env_json, working_dir, module_name, blocking=True, timeout=None):
        env_tmp_file = os.path.join(working_dir, 'apenv.json')
        with open(env_tmp_file, 'w') as f:
            f.write(ap_env_json)
            f.write("\n")
        command = "./" + module_name
        self.log.info("Running command: {0} from repo root dir: {1}".format(command, working_dir))
        return utils.subprocess_cmd(command, working_dir=working_dir, blocking=blocking)


class SafePythonModuleRunner(object):
    """
    Loads user provider python scripts in a different process and runs
    desired actions
    """
    def __init__(self):
        self.log = logger.get_logger("SafePythonModuleRunner")

    # todo: use timeout
    def run(self, ap_env_json, working_dir, module_name, blocking=True, timeout=None):
        env_tmp_file = os.path.join(working_dir, 'apenv.json')
        with open(env_tmp_file, 'w') as f:
            f.write(ap_env_json)
        command = "python -c \"import test; import json; import os; env=json.load(open('{1}')); import {2}; {2}.install(env=env)\"".format(ap_env_json, env_tmp_file, module_name)
        self.log.info("Running python command: {0} from working_dir: {1}".format(command, working_dir))
        return utils.subprocess_cmd(command, working_dir=working_dir, blocking=blocking)


class YumRunner(object):
    """

    """
    def __init__(self):
        self.log = logger.get_logger("YumRunner")