#!/usr/bin/env python3
import os
from aws_cdk import core as cdk

import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ssm as ssm


class KafkaesqueProducerStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster_id = ssm.StringParameter.value_for_string_parameter(self, "my-plain-parameter-name")

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
            memory_limit_mi_b=512,
            cpu=256
        )

        container = task_definition.add_container("WebContainer",
            # Use an image from DockerHub
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
        )

        service = ecs.FargateService(...)


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

