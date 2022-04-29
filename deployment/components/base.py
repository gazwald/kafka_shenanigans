from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ssm as ssm
from constructs import Construct

__all__ = ["BaseConstruct"]


class BaseConstruct(Construct):
    vpc: ec2.IVpc
    ecs_cluster: ecs.ICluster

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id)

    def _set_vpc(self):
        vpc_id: str = ssm.StringParameter.value_from_lookup(
            self, "/common/shared_vpc_id"
        )
        self.vpc: ec2.IVpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)

    def _set_ecs_cluster(self, cluster_name: str):
        self.ecs_cluster: ecs.ICluster = ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=self.vpc, cluster_name=cluster_name, security_groups=[]
        )
