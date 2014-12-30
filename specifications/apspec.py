#! /usr/bin/python
import yaml


class Apspec(object):
    """
    Base class for ApSpec
    todo: We should normalize the spec here into a canonical form
    by replacing undefined values with defaults
    """
    def __init__(self, apenv, org, domain, type, inf=None, description=None):
        self.org = org
        self.domain = domain
        self.apenv = apenv
        self.type = type
        self.inf = inf
        self.description = description

    def todict(self):
        d = dict(org=self.org,
                 domain=self.domain,
                 type=self.type,
                 description=self.description)
        return dict(apspec=d)

    @staticmethod
    def load(apenv, org, domain, spec_stream):
        dct = yaml.load(spec_stream)
        spec_dct = dct.get('apspec')
        func = getattr(Apspec, "_resolve_{0}_spec".format(spec_dct.get('type')))
        return func(apenv, org, domain, spec_dct)

    @staticmethod
    def _resolve_stack_spec(apenv, org, domain, spec_dct):
        return Stackspec(apenv=apenv, org=org, domain=domain, type=spec_dct.get('type'),
                         inf=spec_dct.get('infrastructure'), name=spec_dct.get('name'),
                         description=spec_dct.get('description'),
                         deployd=spec_dct.get('deploy'),
                         groupsd=spec_dct.get("role-groups"))


class Stackspec(Apspec):
    """
    Define the stack
    """
    def __init__(self, apenv, org, domain, type, inf, name, description, deployd, groupsd):
        Apspec.__init__(self, apenv=apenv, org=org, domain=domain,
                        type=type, inf=inf, description=description)
        self.name = name
        self.deploy = StackDeploy(deployd=deployd)
        self.groups = self._resolve_role_groups(groupsd)


    def serialize(self):
        rd = dict()
        for k, g in self.groups.items():
            rd[k] = g.serialize()
        return dict(name=self.name,
                    role_groups=rd)

    def _resolve_role_groups(self, groupsd):
        rg = {}
        for (group, val) in groupsd.items():
            rg[group] = Rolegroup(group, val)
        return rg


class StackDeploy(object):
    def __init__(self, deployd):
        self.git = deployd.get('git')
        self.branch = deployd.get('branch')
        self.metafile = deployd.get('metafile', "meta.yml")

class Rolegroup(object):
    def __init__(self, name, refsd):
        self.name = name
        self.order = refsd.get('order')
        self.instanced = refsd.get('instance')
        self.roles = refsd.get('roles')

    def serialize(self):
        return dict(name=self.name,
                    order=self.order,
                    roles=self.roles,
                    instance=self.instanced)









