#! /usr/bin/python

import os
import unittest
import simplejson
from autopilot.common.sshutils import SSHClient
from autopilot.common.asyncpool import taskpool
from autopilot.common.apenv import ApEnv
from autopilot.workflows.workflow_model import WorkflowModel
from autopilot.inf.aws.awsinf import AWSInf
from autopilot.inf.aws import awsutils
from autopilot.test.common.aptest import APtest


class AWStest(APtest):
    """
    AWS tests base class
    """
    def get_aws_inf(self):
        self.aws_access_key = os.environ["AWS_ACCESS_KEY"]
        self.aws_secret_key = os.environ["AWS_SECRET_KEY"]
        return AWSInf(aws_access_key=self.aws_access_key,
                      aws_secret_key=self.aws_secret_key)

    def delete_vpc(self, spec={}):
        vpc = self. _get_vpc()
        vpc_id = spec.get("vpc_id")

        # delete_dependencies first:
        security_group_id = spec.get("security_group_id", None)
        subnet_id = spec.get("subnet_id", None)
        internet_gateway_id = spec.get("internet_gateway_id", None)
        route_table_id = spec.get("route_table_id", None)
        route_association_id = spec.get("route_association_id", None)

        if security_group_id:
            vpc.conn.delete_security_group(group_id=security_group_id)
        if route_association_id:
            vpc.conn.disassociate_route_table(association_id=route_association_id)
        if route_table_id:
            vpc.conn.delete_route_table(route_table_id=route_table_id)
        if subnet_id:
            vpc.conn.delete_subnet(subnet_id=subnet_id)
        if internet_gateway_id:
            vpc.conn.detach_internet_gateway(internet_gateway_id=internet_gateway_id, vpc_id=vpc_id)
            vpc.conn.delete_internet_gateway(internet_gateway_id=internet_gateway_id)

        # delete the vpc
        vpc.conn.delete_vpc(vpc_id=vpc_id)

    def terminate_instances(self, instance_ids):
        ec2 = self._get_ec2()
        instances = ec2.get_all_instances(instance_ids=instance_ids)
        ec2.terminate_instances(instances=instance_ids)
        self.yield_until_instances_in_state(instances=instances, state="terminated")

    def all_instances_in_state(self, instances, state="running"):
        for instance in instances:
            instance.update()
            # if any instance is pending return True
            if instance.state != state:
                return False
        return True

    def yield_until_instances_in_state(self, instances, state="running", timeout=180, interval=10):
        """
        Yield until all instances are in a specified state
        """
        max_tries = timeout/interval
        attempt = 0
        while attempt < max_tries:
            attempt += 1
            if not self.all_instances_in_state(instances=instances, state=state):
                taskpool.doyield(time_in_seconds=interval)
            else:
                return True
        return False

    def ssh_command(self, host, command="hostname", username="ec2-user", key_pair=None):
        if not key_pair:
            key_pair = os.environ["AP_TEST_AWS_KEY"]

        ssh = SSHClient(host=host, username=username, private_key=key_pair)
        return ssh.execute(command)


    def _get_ec2(self):
        return awsutils.EasyEC2(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        return awsutils.EasyVPC(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")