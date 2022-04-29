from aws_cdk import NestedStack
from components.fargate import FargateTaskConstruct
from constructs import Construct

__all__ = ["ProducerStack"]


class ProducerStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        FargateTaskConstruct(
            self,
            "producer",
            name="producer",
            dockerfile="Dockerfile.producer",
            produce=True,
        )
