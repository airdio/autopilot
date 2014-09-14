#! /usr/bin python


class ApEnv(object):
    """
    Enviroment settings
    """
    def __init__(self, envd={}):
        self.env = envd.copy()

    def add(self, key, value):
        self.env[key] = value

    def get(self, key, default=None):
        return self.env.get(key, default)

    def get_task_resolver(self, wf_id):
        return self.env[wf_id].get("task_resolver", None)

    def add_task_resolver(self, wf_id, resolver):
        self.env[wf_id]["task_resolver"] = resolver

    def remove_task_resolver(self, wf_id):
        self.env[wf_id].pop("task_resolver", None)

    def get_inf_resolver(self, wf_id):
        return self.env[wf_id].get("inf_resolver", None)

    def add_inf_resolver(self, wf_id, resolver):
        self.env[wf_id]["inf_resolver"] = resolver

    def remove_inf_resolver(self, wf_id):
        self.env[wf_id].pop("inf_resolver", None)