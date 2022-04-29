from typing import Optional

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from . import BaseConstruct

_all__ = ["FargateClusterConstruct", "FargateTaskConstruct"]


class FargateClusterConstruct(BaseConstruct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._set_vpc()
        self._set_ecs_cluster("oanda")
        self.ecs_cluster = ecs.Cluster(
            self,
            "fargate",
            cluster_name="oanda",
            vpc=self.vpc,
            enable_fargate_capacity_providers=True,
        )


class FargateTaskConstruct(BaseConstruct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        name: str,
        dockerfile: str = "Dockerfile",
        consume: bool = False,
        produce: bool = False,
    ):
        super().__init__(scope, id)

        self._set_vpc()
        self._set_ecs_cluster("oanda")
        self.create_policies(consume, produce)
        self.task_definition = self.create_task(name, dockerfile)
        self.service = self.create_service(name)

    def create_service(self, name: str):
        return ecs.FargateService(
            self,
            "service",
            cluster=self.ecs_cluster,
            task_definition=self.task_definition,
            assign_public_ip=True,
        )

    def create_task(self, name: str, dockerfile: Optional[str] = None):
        logging = ecs.LogDrivers.aws_logs(
            stream_prefix=name,
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
            name,
            image=ecs.ContainerImage.from_asset(directory=f"../src/", file=dockerfile),
            logging=logging,
        )

        return task_definition

    def create_policies(self, consume: bool = False, produce: bool = False):
        self.kafka_cluster_arn: str = ssm.StringParameter.value_for_string_parameter(
            self, "/oanda/kafka/cluster_arn"
        )
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
            resources=[self.kafka_cluster_arn],
        )

        if consume and not produce:
            self._consumer_policy()
        elif produce and not consume:
            self._producer_policy()
        elif consume and produce:
            self._consumer_producer_policy()

    def _consumer_policy(self):
        self.policy_kafka_cluster = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "kafka-cluster:Connect",
                "kafka-cluster:DescribeTopic",
                "kafka-cluster:ReadData",
            ],
            resources=[
                self.kafka_cluster_arn,
                "arn:aws:kafka:*:*:topic/kafkaesque/*",
            ],
        )

    def _producer_policy(self):
        self.policy_kafka_cluster = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "kafka-cluster:Connect",
                "kafka-cluster:DescribeTopic",
                "kafka-cluster:WriteData",
            ],
            resources=[
                self.kafka_cluster_arn,
                "arn:aws:kafka:*:*:topic/kafkaesque/*",
            ],
        )

    def _consumer_producer_policy(self):
        self.policy_kafka_cluster = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "kafka-cluster:Connect",
                "kafka-cluster:DescribeTopic",
                "kafka-cluster:WriteData",
                "kafka-cluster:ReadData",
            ],
            resources=[
                self.kafka_cluster_arn,
                "arn:aws:kafka:*:*:topic/kafkaesque/*",
            ],
        )
