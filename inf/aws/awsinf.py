#! /user/bin python

from autopilot.common.utils import Dct
from autopilot.inf.inf import Inf, InfResponseContext
from autopilot.inf.aws import awsutils
from autopilot.inf.aws import awsexception


class AWSInfResponseContext(InfResponseContext):
        def __init__(self, spec, callback=None):
            InfResponseContext.__init__(self, spec, callback)

class AWSInf(Inf):
    """
    AWS Infrastructure functions
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
        1. VPC and internet gateway attache to the VPC
        """
        rc = AWSInfResponseContext(stack_spec, callback)
        errors = []
        try:
            # create a vpc and a default internet gateway
            data = self.vpc_conn.create_vpc(cidr_block=Dct.get(stack_spec, "cidr", "10.0.0.0/16"))
            stack_spec["vpc_id"] = data["vpc"].id
            stack_spec["internet_gateway_id"] = data["internet_gateway"].id

        except Exception, e:
            errors.extend(e)

        # return updated spec
        rc.close(stack_spec, errors)
        return rc

    def init_role(self, role_spec={}, callback=None):
        """
        1. Create a subnet for the role with route tables and security groups
        2. Create security group with inbound traffic for 0.0.0.0/0 on port 22 attached to the VPC
           subnet_id=stack_spec["subnet_id"]
        """

        rc = AWSInfResponseContext(role_spec, callback)
        errors = []
        if not Dct.contains_key(role_spec, "vpc_id"):
            raise awsexception.VPCDoesNotExists()

        try:
            # create a subnet within the vpc
            data = self.vpc_conn.create_subnet(vpc_id=role_spec["vpc_id"], cidr_block=Dct.get(role_spec, "cidr", "10.0.0.0/24"),
                                               new_route_table=True, gateway_id=role_spec["internet_gateway_id"],
                                               open_route_to_gateway=True)

            role_spec["subnet_id"] = data["subnet"].id
            role_spec["route_table_id"] = data["route_table"].id

            # # create a security group and attach it to the vpc
            # ec2conn = self._get_ec2()
            # sg = ec2conn.create_group(name="sg_{0}".format(role_spec["uname"]), description=None,
            #                           auth_ssh=True, vpc_id=role_spec["vpc_id"], auth_spec=Dct.get(role_spec, "auth_spec", []))

            # role_spec["security_group_id"] = sg.id
            # self.vpc_conn.associate_gateway_with_subnet(vpc_id=role_spec["vpc_id"], subnet_id=role_spec["subnet_id"],
            #                                            gateway_id=role_spec["internet_gateway_id"])
        except Exception, e:
            #errors.extend(e)
            print "Error is :{0}".format(e)
            raise e

        # return updated spec
        rc.close(role_spec, errors)
        return rc

    def clean_stack(self, env_spec={}, delete_dependencies=False, callback=None):
        """
        Clean up the environment
        """
        self.vpc_conn.delete_vpc(vpc_id=Dct.get(env_spec, "vpc_id"), force=delete_dependencies)

    def provision_role(self, instance_spec={}, tags=[], callback=None):
        """
        Provision a set of machines asynchronously as per spec
        Returns a AWSInfRequestContext context
        """
        sg = self.ec2_conn.create_group("sg_{0}".format(Dct.get(instance_spec, "uname")), description="ap security group",
                              vpc_id=Dct.get(instance_spec, "vpc_id"))
        reservation = self.ec2_conn.request_instances(image_id=instance_spec["image_id"], instance_type=instance_spec["instance_type"],
                                            count=instance_spec["count"], security_group_ids=[sg.id],
                                            subnet_id=instance_spec["subnet_id"])
        return AWSInfResponseContext(instance_spec, self.ec2_conn, reservation)

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