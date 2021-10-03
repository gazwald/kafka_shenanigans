#!/usr/bin/env python3
import os

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_msk as msk
import aws_cdk.aws_ssm as ssm
import boto3
from aws_cdk import core as cdk


class KafkaesqueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = self.get_ssm("/common/shared_vpc_id")
        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)
        isolated_subnets = ec2.SubnetSelection(subnets=vpc.isolated_subnets)

        self.cluster = self.setup_cluster(vpc, isolated_subnets)

        self.create_ssm_parameters()
        self.cluster.add_user("test_user")

    def setup_cluster(
        self,
        vpc: ec2.Vpc,
        subnets: ec2.SubnetSelection,
        instance_class: ec2.InstanceClass = ec2.InstanceClass.BURSTABLE3,
        instance_type: ec2.InstanceSize = ec2.InstanceSize.SMALL,
        volume_size: int = 100,
    ) -> msk.Cluster:
        instance_type = ec2.InstanceType.of(instance_class, instance_type)
        storage = msk.EbsStorageInfo(volume_size=volume_size)

        return msk.Cluster(
            self,
            "cluster",
            cluster_name="kafkaesque",
            instance_type=instance_type,
            kafka_version=msk.KafkaVersion.V2_8_0,
            vpc=vpc,
            vpc_subnets=subnets,
            ebs_storage_info=storage,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            client_authentication=msk.ClientAuthentication.sasl(scram=True),
        )

    def create_ssm_parameters(self):
        attrs = [
            "bootstrap_brokers",
            "bootstrap_brokers_sasl_scram",
            "bootstrap_brokers_tls",
            "zookeeper_connection_string",
            "zookeeper_connection_string_tls",
        ]

        for attr in attrs:
            ssm.StringParameter(
                self,
                attr,
                parameter_name=f"/kafka/{attr}",
                string_value=getattr(self.cluster, attr),
            )

    @staticmethod
    def get_ssm(parameter: str) -> str:
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name=parameter)
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]


def main():
    app = cdk.App()

    KafkaesqueStack(
        app,
        "kafkaesque",
        env=cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="ap-southeast-2"
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
