#!/usr/bin/env python3
import os
import boto3
from aws_cdk import core as cdk

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_msk as msk


class KafkaesqueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=self.get_vpc_id())

        isolated_subnets = ec2.SubnetSelection(subnets=vpc.isolated_subnets)
        instance_type = ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL
        )
        storage = msk.EbsStorageInfo(volume_size=100)

        cluster = msk.Cluster(
            self,
            "cluster",
            cluster_name="kafkaesque",
            instance_type=instance_type,
            kafka_version=msk.KafkaVersion.V2_8_0,
            vpc=vpc,
            vpc_subnets=isolated_subnets,
            ebs_storage_info=storage,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        print(cluster.bootstrap_brokers)

        # cluster.add_user("test_user")

    def get_vpc_id(self):
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name="/common/shared_vpc_id")

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
