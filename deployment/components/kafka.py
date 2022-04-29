from typing import Optional

import aws_cdk.aws_msk_alpha as msk
from aws_cdk import RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from . import BaseConstruct

__all__ = ["KafkaConstruct"]


class KafkaConstruct(BaseConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._set_vpc()
        self.public_subnets = ec2.SubnetSelection(subnets=self.vpc.public_subnets)

        self.msk_cluster = self.setup_cluster()

        self.create_ssm_parameters()

    def setup_cluster(
        self,
        instance_class: ec2.InstanceClass = ec2.InstanceClass.BURSTABLE3,
        instance_size: ec2.InstanceSize = ec2.InstanceSize.SMALL,
        volume_size: Optional[int] = 100,
    ) -> msk.Cluster:
        instance_type: ec2.InstanceType = ec2.InstanceType.of(
            instance_class, instance_size
        )
        security_group = ec2.SecurityGroup(
            self,
            "SecurityGroup",
            vpc=self.vpc,
            description="Kafka access",
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(
            ec2.Peer.ipv4("172.17.0.0/16"), ec2.Port.all_tcp(), "Allow VPC access"
        )
        storage = msk.EbsStorageInfo(volume_size=volume_size)
        monitoring = msk.MonitoringConfiguration(
            cluster_monitoring_level=msk.ClusterMonitoringLevel.PER_TOPIC_PER_BROKER
        )

        return msk.Cluster(
            self,
            "cluster",
            cluster_name="kafkaesque",
            instance_type=instance_type,
            kafka_version=msk.KafkaVersion.V2_8_1,
            vpc=self.vpc,
            vpc_subnets=self.public_subnets,
            ebs_storage_info=storage,
            removal_policy=RemovalPolicy.DESTROY,
            monitoring=monitoring,
            security_groups=[security_group],
        )

    def create_ssm_parameters(self):
        ssm.StringParameter(
            self,
            "cluster-arn",
            parameter_name="/oanda/kafka/cluster_arn",
            string_value=self.msk_cluster.cluster_arn,
        )
