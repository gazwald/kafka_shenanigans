from aws_cdk import NestedStack
from constructs import Construct

from components.fargate import FargateClusterConstruct

__all__ = ["FargateClusterStack"]


class FargateClusterStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        FargateClusterConstruct(self, "fargate")
