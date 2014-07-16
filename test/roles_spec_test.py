#! /usr/bin python

import os
import os.path
import sys
import yaml
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
from autopilot.test.common.aptest import APtest
from autopilot.specifications.apspec import Apspec
from autopilot.common.apenv import ApEnv


class RoleSpecTest(APtest):
    """
    Role Spec tests
    """
    def test_parse_role_spec(self):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing", self.openf('role_spec1.yml'))
        # print rspec.todict()
        self.ae(3, len(rspec.roles))

    def test_parse_min_role_spec(self):
        rspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing", self.openf('role_spec_min.yml'))
        # print rspec.todict()
        self.ae(3, len(rspec.roles))
        self.ae(2.0, rspec.roles["yarn"].version)

    def test_parse_stack_spec(self):
        sspec = Apspec.load(ApEnv(), "contoso.org", "dev.marketing", self.openf('stack_spec1.yml'))
        # print rspec.todict()
        self.ae(2, len(sspec.groups))
        self.ae(2, len(sspec.groups["hadoop"].rolerefs))
        self.ae(5, sspec.groups["hadoop"].rolerefs['hdfs'].instances)
