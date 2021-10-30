#!/usr/bin/env python3
import os

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import boto3
from aws_cdk import core as cdk


class KafkaesqueFargateStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = self.get_ssm("/common/shared_vpc_id")
        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)

        ecs.Cluster(
            self,
            "Cluster",
            cluster_name="oanda",
            vpc=vpc,
            enable_fargate_capacity_providers=True,
        )

    @staticmethod
    def get_ssm(parameter: str) -> str:
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name=parameter)
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]

        return ""


def main():
    app = cdk.App()

    KafkaesqueFargateStack(
        app,
        "fargate",
        env=cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="ap-southeast-2"
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
