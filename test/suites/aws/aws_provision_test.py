#! /usr/bin/python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import gevent
import gevent.monkey
from autopilot.inf.aws.awsinf import AwsInfProvisionResponseContext
from autopilot.test.common.utils import Utils
from autopilot.test.suites.aws.awstest import AWStest
# monkey patch
gevent.monkey.patch_all()


class AwsProvisionTests(AWStest):
    """
    AWS Tests
    """
    def test_aws_provision_response_context(self):
        def update(*args, **kwargs):
            pass
        instance1 = type('', (object, ), {"state": "pending", "update": update})()
        instance2 = type('', (object, ), {"state": "success", "update": update})()
        reservation = type('', (object, ), {"instances": [instance1, instance2]})()
        response = AwsInfProvisionResponseContext({}, reservation=reservation)
        self.af(self.pool(response.close_on_instances_ready,
                          args=dict(timeout=1, interval=1), wait_timeout=3).get())

        instance1 = type('', (object, ), {"state": "running", "update": update})()
        instance2 = type('', (object, ), {"state": "running", "update": update})()
        reservation = type('', (object, ), {"instances": [instance1, instance2]})()
        response = AwsInfProvisionResponseContext({}, reservation=reservation)
        self.log("Waiting for response to finish")
        self.at(self.pool(response.close_on_instances_ready,
                          args=dict(timeout=1, interval=1), wait_timeout=3).get())

    def test_init_domain(self):
        a = self.get_aws_inf()
        domain_spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "any.aptest.com",
        }

        try:
            rc = a.init_domain(domain_spec=domain_spec)
            self.fail_on_errors(rc)
            self.at(len(rc.spec["vpc_id"]) > 0, "vpc_id")
            self.at(len(rc.spec["internet_gateway_id"]) > 0, "internet_gateway_id")
        finally:
            self.delete_vpc(domain_spec)
            pass

    def test_init_stack(self):
        """
        test stack initialization
        """
        a = self.get_aws_inf()
        domain_spec = {
            #"uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "uname": "used_for_aptest_only",
            "domain": "any.aptest.com",
        }
        rc_stack = None
        try:
            rc_domain = a.init_domain(domain_spec=domain_spec)
            stack_spec = {
                #"uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "uname": "used_for_aptest_only",
                "vpc_id": rc_domain.spec["vpc_id"],
                "internet_gateway_id": rc_domain.spec["internet_gateway_id"],
                "cidr": "10.0.0.0/24"
            }
            rc_stack = a.init_stack(domain_spec=domain_spec, stack_spec=stack_spec)
            self.fail_on_errors(rc_stack)

            subnets = rc_stack.spec["subnets"]
            first_subnet = subnets[0]
            self.ae(1, len(subnets), "subnets")
            self.at(first_subnet.get("subnet_id"))
            self.at(first_subnet.get("route_table_id"))
            self.at(first_subnet.get("route_association_id"))
            print rc_stack.spec
        finally:
            self.delete_vpc(rc_stack.spec)
            pass

    def test_instance_provision(self):
        """
        Test instance provision
        """
        aws_inf = self.get_aws_inf()
        rc_instances = None
        try:
            domain_spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
            "vpc_id": "vpc-5c0eab39",
            "internet_gateway_id": "igw-c96eaaac",
            }
            stack_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "cidr": "10.0.0.0/24",
                "subnets": ["subnet-434b4d6b"]
            }
            instance_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "image_id": "ami-a25415cb",
                "instance_type": "m1.medium",
                "key_pair_name": "ocg-test",
                "instance_count": 2,
                "associate_public_ip": True,
                "auth_spec": [{"protocol": "tcp", "from": 80, "to": 80},
                              {"protocol": "tcp", "from": 3306, "to": 3306}],
            }
            rc_instances = aws_inf.provision_instances(domain_spec=domain_spec, stack_spec=stack_spec,
                                                       instance_spec=instance_spec)

            self.fail_on_errors(rc_instances)

            instances = rc_instances.spec.get("instances")
            self.at(rc_instances.spec["security_group_ids"])
            self.ae(2, len(instances))
            self.at(instances[0].get('public_dns_name'))
            self.at(instances[0].get('private_dns_name'))
            self.at(instances[0].get('public_ip_address'))
            self.at(instances[0].get('private_ip_address'))
            self.at(instances[1].get('public_dns_name'))
            self.at(instances[1].get('private_dns_name'))
            self.at(instances[1].get('public_ip_address'))
            self.at(instances[1].get('private_ip_address'))
        finally:
            if rc_instances:
                self.terminate_instances(rc_instances.spec)
            pass