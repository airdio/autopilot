#! /user/bin python

import time
from autopilot.common import exception
from autopilot.common.utils import Dct
from autopilot.common.asyncpool import taskpool
from autopilot.inf.inf import Inf, InfResponseContext
from autopilot.inf.aws import awsutils
from autopilot.inf.aws import awsexception


class AWSInfResponseContext(InfResponseContext):
    def __init__(self, aws_inf, spec):
        """
        Response context base class for tracking AWS resquests
        """
        InfResponseContext.__init__(self, spec)


class AwsInfProvisionResponseContext(AWSInfResponseContext):
    """
    Response Context object to track AWS instance provisioning requests
    """
    def __init__(self, aws_inf, spec, reservation):
        AWSInfResponseContext.__init__(self, aws_inf=aws_inf, spec=spec)
        self.reservation = reservation

    def are_any_instances_pending(self):
        for instance in self.reservation.instances:
            instance.update()
            # if any instance is pending return True
            if instance.state == "pending":
                return True
        return False

    def close_on_instances_ready(self, timeout=180, interval=10):
        """
        Close when all instances are non-pending
        """
        if self.yield_until_instances_ready(timeout=timeout, interval=interval):
            self.close()
        else:
            self.close(new_errors=[exception.AWSInstanceProvisionTimeout(self.reservation.instances)])

    def yield_until_instances_ready(self, timeout=180, interval=10):
        """
        Associate network interfaces with public ips to instances once they are up
        """
        max_tries = timeout/interval
        attempt = 0
        while attempt < max_tries:
            attempt += 1
            if self.are_any_instances_pending():
                taskpool.doyield(time_in_seconds=interval)
            else:
                return True

        return False


class AWSInf(Inf):
    """
    AWS Infrastructure management functions

    All wait and test actions following aws api calls are all pumped through the gevent and
    should yield if we have monkey patched somewhere along the call chain.
    """
    def __init__(self, aws_access_key=None, aws_secret_key=None):
        Inf.__init__(self)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.vpc_conn = self._get_vpc()
        self.ec2_conn = self._get_ec2()

    def init_stack(self, stack_spec={}):
        """
        Create a deployment environment based on the spec.
        At minimum this will create:
        1. VPC
        2. Internet gateway with internet routing enabled and attach to the VPC
        """
        rc = AWSInfResponseContext(aws_inf=self, spec=stack_spec)
        try:
            # create a vpc and a default internet gateway
            data = self.vpc_conn.create_vpc(cidr_block=Dct.get(stack_spec, "cidr", "10.0.0.0/16"))
            stack_spec["vpc_id"] = data["vpc"].id
            stack_spec["internet_gateway_id"] = data["internet_gateway"].id

        except Exception, e:
            rc.errors.extend(e)

        # return updated spec
        rc.close(stack_spec)
        return rc

    def init_role(self, role_spec={}):
        """
        We need a VPC in the role_spec that we can use
        Create a subnet for the role with route tables and security groups
        """
        rc = AWSInfResponseContext(aws_inf=self, spec=role_spec)
        if not Dct.contains_key(role_spec, "vpc_id"):
            raise awsexception.VPCDoesNotExists()

        try:
            # create a subnet within the vpc
            data = self.vpc_conn.create_subnet(vpc_id=role_spec["vpc_id"], cidr_block=Dct.get(role_spec, "cidr", "10.0.0.0/24"),
                                               new_route_table=True, gateway_id=role_spec["internet_gateway_id"],
                                               open_route_to_gateway=True)

            role_spec["subnet_id"] = data["subnet"].id
            role_spec["route_table_id"] = data["route_table"].id
        except Exception, e:
            rc.errors.extend(e)

        # return updated spec
        rc.close(role_spec)
        return rc

    def clean_stack(self, env_spec={}, delete_dependencies=False):
        """
        Clean up the environment
        """
        self.vpc_conn.delete_vpc(vpc_id=Dct.get(env_spec, "vpc_id"), force=delete_dependencies)

    def provision(self, instance_spec={}, tags=[]):
        """
        We need a subnet in the the instance_spec
        1. Create default security group with inbound traffic for:
            a. 22-22 (0.0.0.0/0)
            b. Custom auth_spec
        2. Provision a set of machines asynchronously as per spec.
        Returns a AWSInfRequestContext context
        """

        # required parameters
        uname = Dct.get(instance_spec, "uname")
        image_id = Dct.get(instance_spec, "image_id")
        instance_type = Dct.get(instance_spec, "instance_type")
        vpc_id = Dct.get(instance_spec, "vpc_id")
        subnet_id = Dct.get(instance_spec, "subnet_id")
        instance_count = Dct.get(instance_spec, "instance_count")
        associate_public_ip = Dct.get(instance_spec, "associate_public_ip", False)

        # create a security group
        sg = self.ec2_conn.create_group("sg_{0}".format(uname),
                                        description="security group for {0}".format(uname),
                                        auth_ssh=True, vpc_id=vpc_id,
                                        auth_spec=Dct.get(instance_spec, "auth_spec"))

        instance_spec["security_group_ids"] = [sg.id]

        # schedule instance creation.
        reservation = self.ec2_conn.request_instances(image_id=image_id,
                                                      instance_type=instance_type,
                                                      max_count=instance_count,
                                                      security_group_ids=instance_spec["security_group_ids"],
                                                      subnet_id=subnet_id,
                                                      associate_public_ip=associate_public_ip)

        instance_spec["instance_ids"] = [instance.id for instance in reservation.instances]

        # create a response context
        rc = AwsInfProvisionResponseContext(aws_inf=self, spec=instance_spec, reservation=reservation)

        # At this point the instances might not be fully ready. But we still call associate_public_ip
        # which will wait for instances to be ready and then try to give a public ip to each instance
        # this works because if use gevent.sleep to yield
        if associate_public_ip:
            errors = self._associate_public_ip(response_context=rc)
            rc.close(new_errors=errors)
        else:
            rc.close_on_instances_ready()

        # return the context
        return rc

    def _associate_public_ip(self, response_context):
        """
        Associate network interfaces with public ips to instances once they are up
        """
        errors = []
        reservation =response_context.reservation
        if response_context.yield_until_instances_ready():
            self.ec2_conn.associate_public_ips(instances=reservation.instances,
                                                subnet_id=response_context.spec["subnet_id"],
                                                security_group_ids=response_context.spec["security_group_ids"])
        else:
            errors.extend(exception.AWSInstanceProvisionTimeout(reservation.instances))

        return errors

    def _get_ec2(self):
        return awsutils.EasyEC2(aws_access_key_id = self.aws_access_key,
                                aws_secret_access_key = self.aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        return awsutils.EasyVPC(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")