#!/usr/bin/env python3
import os

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_logs as logs
import boto3
from aws_cdk import core as cdk


class ConsumerConstruct(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str, name, cluster, prefix=None):
        super().__init__(scope, id)

        self.create_policies()
        self.task_definition = self.create_task(name)
        self.service = self.create_service(name, cluster)

    def create_service(self, name, cluster):
        return ecs.FargateService(
            self,
            name + "service",
            cluster=cluster,
            task_definition=self.task_definition,
            assign_public_ip=True,
        )

    def create_task(self, name):
        logging = ecs.LogDrivers.aws_logs(
            stream_prefix=name + "consumer",
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        task_definition = ecs.FargateTaskDefinition(
            self, name + "task", memory_limit_mib=512, cpu=256
        )

        task_definition.add_to_task_role_policy(self.policy_ssm)
        task_definition.add_to_task_role_policy(self.policy_glue)
        task_definition.add_to_task_role_policy(self.policy_kafka)
        task_definition.add_to_task_role_policy(self.policy_kafka_cluster)

        task_definition.add_container(
            name + "consumer",
            image=ecs.ContainerImage.from_asset(f"./{name}-image"),
            logging=logging,
        )

        return task_definition

    def create_policies(self):
        self.policy_ssm = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["ssm:Describe*", "ssm:Get*", "ssm:List*"],
            resources=["arn:aws:ssm:*:*:parameter/oanda/*"],
        )
        self.policy_glue = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["glue:GetSchemaVersion"],
            resources=[
                "arn:aws:glue:*:*:registry/oanda",
                "arn:aws:glue:*:*:schema/oanda/instrument",
            ],
        )
        self.policy_kafka = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["kafka:GetBootstrapBrokers"],
            resources=[self.get_ssm("/oanda/kafka/cluster_arn")],
        )
        self.policy_kafka_cluster = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "kafka-cluster:Connect",
                "kafka-cluster:DescribeTopic",
                "kafka-cluster:ReadData",
            ],
            resources=[
                self.get_ssm("/oanda/kafka/cluster_arn"),
                "arn:aws:kafka:*:*:topic/kafkaesque/*",
            ],
        )

    @staticmethod
    def get_ssm(parameter: str) -> str:
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name=parameter)
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]

        return ""


class KafkaesqueConsumerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = self.get_ssm("/common/shared_vpc_id")
        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)
        cluster = ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=vpc, cluster_name="oanda", security_groups=[]
        )

        ConsumerConstruct(self, "test", name="test", cluster=cluster)

    @staticmethod
    def get_ssm(parameter: str) -> str:
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name=parameter)
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]

        return ""


def main():
    app = cdk.App()

    KafkaesqueConsumerStack(
        app,
        "consumers",
        env=cdk.Environment(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="ap-southeast-2"
        ),
    )

    app.synth()


if __name__ == "__main__":
    main()
