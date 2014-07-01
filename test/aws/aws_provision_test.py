#! /usr/bin/python

import os
import os.path
import sys
sys.path.append(os.environ['AUTOPILOT_HOME'] + '/../')
import gevent
import gevent.monkey
from autopilot.common.apenv import ApEnv
from autopilot.inf.aws.awsinf import AwsInfProvisionResponseContext
from autopilot.workflows.tasks.task import TaskState
from autopilot.workflows.workflowexecutor import WorkflowExecutor
from autopilot.workflows.workflowmodel import WorkflowModel
from autopilot.stack.tasks.deployrole import AWSDeployRole, AWSDomainInit, AWSStackInit
from autopilot.test.common.utils import Utils
from autopilot.test.aws.awstest import AWStest



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
        self.af(response.wait(timeout=2, interval=1))

        instance1 = type('', (object, ), {"state": "success", "update": update})()
        instance2 = type('', (object, ), {"state": "success", "update": update})()
        reservation = type('', (object, ), {"instances": [instance1, instance2]})()
        response = AwsInfProvisionResponseContext({}, reservation=reservation)
        self.at(response.wait(timeout=2, interval=1))

    def test_init_domain(self):
        a = self.get_aws_inf()
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }

        try:
            rc = a.init_domain(spec)
            self.ae(len(rc.errors), 0, "errors found")
            self.at(len(rc.spec["vpc_id"]) > 0, "vpc_id")
            self.at(len(rc.spec["internet_gateway_id"]) > 0, "internet_gateway_id")
        finally:
            self.delete_vpc(spec)

    def test_init_stack(self):
        """
        test stack initialization
        """
        a = self.get_aws_inf()
        spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }
        rc_stack = None
        try:
            rc_domain = a.init_domain(spec)
            stack_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "vpc_id": rc_domain.spec["vpc_id"],
                "internet_gateway_id": rc_domain.spec["internet_gateway_id"],
                "cidr": "10.0.0.0/24",
                "subnets": rc_domain.spec["subnets"]
            }
            rc_stack = a.init_stack(stack_spec)
            subnets = rc_stack.spec["subnets"]
            first_subnet = subnets[0]

            self.ae(0, len(rc_stack.errors), "errors found")
            self.ae(1, len(subnets), "subnets")
            self.at(first_subnet.get("subnet_id"))
            self.at(first_subnet.get("route_table_id"))
            self.at(first_subnet.get("route_association_id"))
        finally:
            if rc_stack:
                self.delete_vpc(rc_stack.spec)

    def test_instance_provision(self):
        """
        Test instance provision
        """
        aws_inf = self.get_aws_inf()
        domain_spec = {
            "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
            "domain": "*.aptest.com",
        }
        reservation = None
        rc_instances = None
        try:
            rc_domain = aws_inf.init_domain(domain_spec)
            stack_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "vpc_id": rc_domain.spec["vpc_id"],
                "internet_gateway_id": rc_domain.spec["internet_gateway_id"],
                "cidr": "10.0.0.0/24",
                "subnets": rc_domain.spec["subnets"]
            }
            rc_stack = aws_inf.init_stack(stack_spec)
            subnets = rc_stack.spec["subnets"]
            first_subnet = subnets[0]

            role_spec = {
                "uname": "test_{0}".format(Utils.get_utc_now_seconds()),
                "image_id": "ami-a25415cb",
                "instance_type": "m1.medium",
                "key_pair_name": "aptest",
                "instance_count": 2,
                "vpc_id": rc_stack.spec["vpc_id"],
                "subnet_id": first_subnet.get("subnet_id"),
                "route_table_id": first_subnet.get("route_table_id"),
                "route_association_id": first_subnet.get("route_association_id"),
                "associate_public_ip": True,
                "auth_spec": [{"protocol": "tcp", "from": 80, "to": 80},
                              {"protocol": "tcp", "from": 3306, "to": 3306}],
            }
            rc_instances = aws_inf.provision_role(role_spec)
            reservation = rc_instances.spec["reservation"]

            self.at(rc_instances.spec["security_group_ids"])
            self.ae(2, len(reservation.instances))
            # self.at(len(self.ssh_command(host=instances[0].ip_address)) > 0)
        finally:
            pass
            if reservation and reservation.instances:
                self.terminate_instances([instance.id for instance in reservation.instances])
            #if rc_instances.spec:
                #self.delete_vpc(rc_instances.spec)

    def test_deploy_role(self):
        (model, ex) = self.get_default_model("stack_deploy1.yml")
        model.inf["properties"]["aws_access_key_id"] = os.environ["AWS_ACCESS_KEY"]
        model.inf["properties"]["aws_secret_access_key"] = os.environ["AWS_SECRET_KEY"]

        ex.workflow_state = {
                  "domain": {
                      "spec": {},
                  },
                  "stack": {
                      "spec": {}
                  },
                  "roles": {
                  },
        }
        instances = None
        try:
            ex.execute()
            # self.ae(True, ex.success)
            # for group in model.groupset.groups:
            #     for task in group.tasks:
            #         self.ae(TaskState.Done, task.result.state, "task should be in Done state")
            # rc_instances = {}
            # self.at(rc_instances.spec["security_group_ids"])
            # self.ae(2, len(instances))
        finally:
            # if instances:
            #     self.terminate_instances([instance.id for instance in instances])
            pass


    def get_AWSDeployRole(self, apenv, inf, wf_id, properties, workflow_state):
        return AWSDeployRole(apenv, wf_id, inf, properties, workflow_state)

    def get_AWSDomainInit(self, apenv, inf, wf_id, properties, workflow_state):
        return AWSDomainInit(apenv, wf_id, inf, properties, workflow_state)

    def get_AWSStackInit(self, apenv, inf, wf_id, properties, workflow_state):
        return AWSStackInit(apenv, wf_id, inf, properties, workflow_state)

