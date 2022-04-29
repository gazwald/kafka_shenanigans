from aws_cdk import Stack
from constructs import Construct
from stacks import (
    ConsumerStack,
    FargateClusterStack,
    GlueStack,
    KafkaStack,
    ProducerStack,
)

__all__ = ["KafkaesqueStack"]


class KafkaesqueStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fargate = FargateClusterStack(self, "fargate")
        kafka = KafkaStack(self, "kafka")
        glue = GlueStack(self, "glue")

        producer = ProducerStack(self, "producer")
        producer.add_dependency(fargate)
        producer.add_dependency(kafka)
        producer.add_dependency(glue)

        consumer = ConsumerStack(self, "consumer")
        consumer.add_dependency(fargate)
        consumer.add_dependency(kafka)
        consumer.add_dependency(glue)
