#! /user/bin python

import time
from autopilot.common import exception
from autopilot.common.utils import Dct
from autopilot.common.asyncpool import taskpool
from autopilot.inf.inf import Inf, InfResponseContext
from autopilot.inf.aws import awsutils
from autopilot.inf.aws import awsexception


class AWSInfResponseContext(InfResponseContext):
    def __init__(self, aws_inf, spec, callback=None):
        """
        Response context base class for tracking AWS resquests
        """
        InfResponseContext.__init__(self, spec, callback)


class AwsInfProvisionResponseContext(AWSInfResponseContext):
    """
    Response Context object to track AWS instance provisioning requests
    """
    def __init__(self, aws_inf, spec, reservation, callback=None):
        AWSInfResponseContext.__init__(self, aws_inf=aws_inf, spec=spec, callback=callback)
        self.reservation = reservation

    def _blocking_wait_for_instances(self, timeout=180, interval=5):
        """
        Should only use for testing. Production code should not call this
        """
        # is already closed
        if self.closed:
            return True

        tries = timeout/interval
        pending = True
        while tries > 0 and pending:
            tries -= 1
            time.sleep(interval)
            pending = self.are_any_instances_pending()

        # false indicates that the task was not a success even after
        # specified wait
        return not pending

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
        max_tries = timeout/interval

        def try_close(attempt=1):
            if attempt > max_tries:
                # we timed out
                self.close(errors=[exception.AWSInstanceProvisionTimeout(self.reservation.instances)])
            else:
                if self.are_any_instances_pending():
                    taskpool.spawn(func=try_close, callback=None, delay=interval, attempt=attempt+1)
                else:
                    self.close()
        try_close()


class AWSInf(Inf):
    """
    AWS Infrastructure management functions
    """
    def __init__(self, aws_access_key=None, aws_secret_key=None):
        Inf.__init__(self)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.vpc_conn = self._get_vpc()
        self.ec2_conn = self._get_ec2()

    def init_stack(self, stack_spec={}, callback=None):
        """
        Create a deployment environment based on the spec.
        At minimum this will create:
        1. VPC
        2. Internet gateway with internet routing enabled and attach to the VPC
        """
        rc = AWSInfResponseContext(aws_inf=self, spec=stack_spec, callback=callback)
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

    def init_role(self, role_spec={}, callback=None):
        """
        We need a VPC in the role_spec that we can use
        Create a subnet for the role with route tables and security groups
        """
        rc = AWSInfResponseContext(aws_inf=self, spec=role_spec, callback=callback)
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

    def clean_stack(self, env_spec={}, delete_dependencies=False, callback=None):
        """
        Clean up the environment
        """
        self.vpc_conn.delete_vpc(vpc_id=Dct.get(env_spec, "vpc_id"), force=delete_dependencies)

    def provision(self, instance_spec={}, tags=[], callback=None):
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

        reservation = self.ec2_conn.request_instances(image_id=image_id,
                                                      instance_type=instance_type,
                                                      count=instance_count, security_group_ids=[sg.id],
                                                      subnet_id=subnet_id,
                                                      associate_public_ip=associate_public_ip)

        # create a response context
        rc = AwsInfProvisionResponseContext(aws_inf=self, spec=instance_spec, reservation=reservation, callback=callback)
        if associate_public_ip:
            self._associate_public_ip(response_context=rc)
        else:
            rc.close_on_instances_ready()

        # we are not guaranteed that the instances are up here
        # return the context so that the caller can either wait or process callback
        return rc

    def _associate_public_ip(self, response_context, timeout=180, interval=10):
        """
        Associate network interfaces with public ips to instances once they are up
        """
        max_tries = timeout/interval

        def try_attach_network_interfaces(attempt=1):
            if attempt > max_tries:
                # we timed out
                response_context.close(errors=[exception.AWSInstanceProvisionTimeout(response_context.reservation.instances)])
            else:
                if response_context.are_any_instances_pending():
                    taskpool.spawn(func=try_attach_network_interfaces, callback=None,
                                   delay=interval, attempt=attempt+1)
                else:
                    # ready. attach network interfaces and close
                    response_context.close()

        try_attach_network_interfaces()

    def _get_ec2(self):
        return awsutils.EasyEC2(aws_access_key_id = self.aws_access_key,
                                aws_secret_access_key = self.aws_secret_key, aws_region_name="us-east-1")

    def _get_vpc(self):
        return awsutils.EasyVPC(aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key, aws_region_name="us-east-1")

# import time
# import boto
# import boto.ec2.networkinterface
#
# from settings.settings import AWS_ACCESS_GENERIC
#
# ec2 = boto.connect_ec2(*AWS_ACCESS_GENERIC)
#
# interface = boto.ec2.networkinterface.NetworkInterfaceSpecification(subnet_id='subnet-11d02d71',
#                                                                     groups=['sg-0365c56d'],
#                                                                     associate_public_ip_address=True)
# interfaces = boto.ec2.networkinterface.NetworkInterfaceCollection(interface)
#
# reservation = ec2.run_instances(image_id='ami-a1074dc8',
#                                 instance_type='t1.micro',
#                                 #the following two arguments are provided in the network_interface
#                                 #instead at the global level !!
#                                 #'security_group_ids': ['sg-0365c56d'],
#                                 #'subnet_id': 'subnet-11d02d71',
#                                 network_interfaces=interfaces,
#                                 key_name='keyPairName')
#
# instance = reservation.instances[0]
# instance.update()
# while instance.state == "pending":
#     print instance, instance.state
#     time.sleep(5)
#     instance.update()
#
# instance.add_tag("Name", "some name")
#
# print "done", instance