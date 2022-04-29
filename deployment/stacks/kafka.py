from aws_cdk import NestedStack
from constructs import Construct

from components.kafka import KafkaConstruct

__all__ = ["KafkaStack"]


class KafkaStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        KafkaConstruct(self, "kafka")
