#!/usr/bin/env python3
import os
from aws_cdk import core as cdk

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_msk as msk
import aws_cdk.aws_ssm as ssm


class KafkaesqueStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = ssm.StringParameter.value_for_string_parameter(self, "/common/shared_vpc_id")
        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)
        isolated_subnets = ec2.SubnetSelection(subnets=vpc.isolated_subnets)

        cluster = self.setup_cluster(vpc, isolated_subnets)
        bastion = self.setup_bastion(vpc, isolated_subnets)

        print(cluster.bootstrap_brokers)

        # cluster.add_user("test_user")

    def setup_cluster(self, vpc: ec2.Vpc, subnets: ec2.SubnetSelection) -> msk.Cluster:
        instance_type = ec2.InstanceType.of(
            ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL
        )
        storage = msk.EbsStorageInfo(volume_size=100)

        return msk.Cluster(
            self,
            "cluster",
            cluster_name="kafkaesque",
            instance_type=instance_type,
            kafka_version=msk.KafkaVersion.V2_8_0,
            vpc=self.vpc,
            vpc_subnets=subnets,
            ebs_storage_info=storage,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

    def setup_bastion(
        self, vpc: ec2.Vpc, subnets: ec2.SubnetSelection
    ) -> ec2.BastionHostLinux:
        return ec2.BastionHostLinux(
            self, "BastionHost", vpc=vpc, subnet_selection=subnets
        )


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
