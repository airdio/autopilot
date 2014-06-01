#! /user/bin python

from autopilot.common.utils import Dct
from autopilot.inf.inf import Inf, InfRequestContext
from autopilot.inf.aws import awsutils


class AWSInfRequestContext(InfRequestContext):
        def __init__(self, spec, callback=None):
            InfRequestContext.__init__(self, spec, callback)


class AWSInf(Inf):
    """
    AWS Infrastructure functions
    """
    def __init__(self, aws_access_key=None,
                 aws_secret_key=None):
        Inf.__init__(self)
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.vpc_conn = self._get_vpc()
        self.ec2_conn = self._get_ec2()

    def new_env(self, env_spec={}, callback=None):
        """
        Create a deployment environment based on the spec.
        At minimum this will create:
        1. VPC and internet gateway attache to the VPC
        2. Security group with inbound traffic for 0.0.0.0/0 on port 22
           attached to the VPC
        3. A subnet
        4. Create a new key_pair ???
        """
        # create a vpc
        vpc = self.vpc_conn.create_vpc(cidr_block=Dct.get(env_spec, "cidr", "10.0.0.0/16"))
        env_spec["vpc_id"] = vpc.id

        # create a subnet within the vpc
        subnet = self.vpc_conn.create_subnet(vpc_id=env_spec["vpc_id"], cidr_block=Dct.get(env_spec, "cidr", "10.0.0.0/24"))
        env_spec["subnet_id"] = subnet.id

        # setup routes and internet gateway so that instances inside the vpc can route outside the vpc
        igw = self.vpc_conn.create_and_associate_internet_gateway(vpc_id=env_spec["vpc_id"], subnet_id=env_spec["subnet_id"])
        env_spec["internet_gateway_id"] = igw.id

        # create a security group and attach it to the vpc
        ec2conn = self._get_ec2()
        sg = ec2conn.create_group(name="sg_{0}".format(env_spec["uname"]), description=None,
                                  auth_ssh=True, vpc_id=env_spec["vpc_id"], auth_spec=Dct.get(env_spec, "auth_spec", []))

        env_spec["security_group_id"] = sg.id

        # return updated spec
        return AWSInfRequestContext(env_spec, callback)

    def clean_env(self, env_spec={}, callback=None):
        """
        Clean up the environemnt
        """
        self.vpc_conn.delete_vpc(vpc_id=Dct.get(env_spec, "vpc_id"))

    def new_instance(self, instance_spec={}, tags=[], callback=None):
        """
        Provision a set of machines asynchronously as per spec
        Returns a AWSInfRequestContext context
        """
        sg = self.ec2_conn.create_group("sg_{0}".format(Dct.get(instance_spec, "uname")), description="ap security group",
                              vpc_id=Dct.get(instance_spec, "vpc_id"))
        reservation = self.ec2_conn.request_instances(image_id=instance_spec["image_id"], instance_type=instance_spec["instance_type"],
                                            count=instance_spec["count"], security_group_ids=[sg.id],
                                            subnet_id=instance_spec["subnet_id"])
        return AWSInfRequestContext(instance_spec, self.ec2_conn, reservation)

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