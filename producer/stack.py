#!/usr/bin/env python3
import os

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import boto3
from aws_cdk import core as cdk


class KafkaesqueProducerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = self.get_ssm("/common/shared_vpc_id")
        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)
        cluster = ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=vpc, cluster_name="oanda", security_groups=[]
        )

        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=512, cpu=256
        )

        task_definition.add_container(
            "Producer", image=ecs.ContainerImage.from_asset("./image")
        )

        ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=task_definition,
        )

    @staticmethod
    def get_ssm(parameter: str) -> str:
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name=parameter)
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]


def main():
    app = cdk.App()

    KafkaesqueProducerStack(
        app,
        "producer",
        env=cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="ap-southeast-2"
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
