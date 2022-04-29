from aws_cdk import NestedStack
from components.fargate import FargateTaskConstruct
from constructs import Construct

__all__ = ["ConsumerStack"]


class ConsumerStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        FargateTaskConstruct(
            self,
            "consumer",
            name="consumer",
            dockerfile="Dockerfile.consumer",
            consume=True,
        )
