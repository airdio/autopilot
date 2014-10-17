#! /usr/bin/python

import os
from autopilot.common.sshutils import SSHClient
from autopilot.common.asyncpool import taskpool
from autopilot.inf.aws.awsinf import AWSInf
from autopilot.inf.aws import awsutils
from autopilot.test.common.aptest import APtest


class AWStest(APtest):
    """
    AWS tests base class
    """
    def get_aws_inf(self):
        aws_access_key = os.environ["AWS_ACCESS_KEY"]
        aws_secret_key = os.environ["AWS_SECRET_KEY"]
        return AWSInf(aws_access_key=aws_access_key,
                      aws_secret_key=aws_secret_key)

    def delete_vpc_subnets(self, spec=None):
        vpc = self. _get_vpc()
        # disassociate all subnets and subnet related resources
        subnets = spec.get("subnets", [])
        if subnets:
            for subnet in subnets:
                sid = subnet.get("subnet_id")
                raid = subnet.get("route_association_id")
                rtid = subnet.get("route_table_id")

                self.log("Deleting resources for subnet: {0}".format(sid))
                if raid:
                    self.log("Disassociate route {0} for subnet: {1}".format(raid, sid))
                    vpc.conn.disassociate_route_table(association_id=raid)
                if rtid:
                    self.log("Delete route {0} for subnet: {1}".format(rtid, sid))
                    vpc.conn.delete_route_table(route_table_id=rtid)

                self.log("Deleting subnet: {0}".format(sid))
                vpc.conn.delete_subnet(subnet_id=sid)

    def terminate_instances(self, spec=None):
        ec2 = self._get_ec2()
        instances = spec.get("instances")
        instance_ids = [instance.get("instance_id") for instance in instances]
        self.log("Terminating instances: {0}".format(instance_ids))
        self.terminate_instances_by_ids(instance_ids=instance_ids)

        sgids = spec.get("security_group_ids")
        if sgids:
            for sgid in sgids:
                self.log("Deleting security group: {0}".format(sgid))
                ec2.delete_group(group_id=sgid, retry_count=24)

    def terminate_instances_by_ids(self, instance_ids):
        ec2 = self._get_ec2()
        instances = ec2.get_all_instances(instance_ids=instance_ids)
        ec2.terminate_instances(instances=instance_ids)
        self.yield_until_instances_in_state(instances=instances, state="terminated")
        self.doyield()

    def delete_vpc(self, spec=None):
        vpc = self. _get_vpc()

        # disassociate all subnets and subnet related resources
        self.delete_vpc_subnets(spec=spec)

        vpc_id = spec.get("vpc_id")
        security_group_id = spec.get("security_group_id", None)
        internet_gateway_id = spec.get("internet_gateway_id", None)
        route_table_id = spec.get("route_table_id", None)
        route_association_id = spec.get("route_association_id", None)
        if security_group_id:
            vpc.conn.delete_security_group(group_id=security_group_id)
        if route_association_id:
            vpc.conn.disassociate_route_table(association_id=route_association_id)
        if route_table_id:
            vpc.conn.delete_route_table(route_table_id=route_table_id)
        if internet_gateway_id:
            vpc.conn.detach_internet_gateway(internet_gateway_id=internet_gateway_id, vpc_id=vpc_id)
            vpc.conn.delete_internet_gateway(internet_gateway_id=internet_gateway_id)

        # delete the vpc
        vpc.conn.delete_vpc(vpc_id=vpc_id)

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
                taskpool.doyield(seconds=interval)
            else:
                return True
        return False

    def ssh_command(self, host, command="hostname", username="ec2-user", key_pair=None):
        if not key_pair:
            key_pair = os.environ["AP_TEST_AWS_KEY"]

        ssh = SSHClient(host=host, username=username, private_key=key_pair)
        return ssh.execute(command)

    def fail_on_errors(self, provision_spec):
        if provision_spec.errors:
            for error in provision_spec.errors:
                self.log(error.message, error=True)
            self.fail("Errors. Count: {0}".format(len(provision_spec.errors)))

    def _get_ec2(self):
        aws_access_key = os.environ["AWS_ACCESS_KEY"]
        aws_secret_key = os.environ["AWS_SECRET_KEY"]
        return awsutils.EasyEC2(aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        aws_access_key = os.environ["AWS_ACCESS_KEY"]
        aws_secret_key = os.environ["AWS_SECRET_KEY"]
        return awsutils.EasyVPC(aws_access_key_id=aws_access_key,
                                aws_secret_access_key=aws_secret_key, aws_region_name="us-east-1")