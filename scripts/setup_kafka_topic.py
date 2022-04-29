#!/usr/bin/env python3
import os

from boto3.session import Session
from kafka.admin import KafkaAdminClient, NewTopic
from mypy_boto3_glue.client import GlueClient
from mypy_boto3_kafka.client import KafkaClient
from mypy_boto3_kafka.type_defs import GetBootstrapBrokersResponseTypeDef

from shared import get_ssm

REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
glue: GlueClient = Session().client("glue", region_name=REGION)
msk: KafkaClient = Session().client("kafka", region_name=REGION)


def main():
    bootstrap_servers: GetBootstrapBrokersResponseTypeDef = msk.get_bootstrap_brokers(
        ClusterArn=get_ssm("/oanda/kafka/cluster_arn")
    )

    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers["BootstrapBrokerStringSaslIam"],
        client_id=os.getenv("APP_NAME", "oanda_topic_creator"),
        security_protocol=os.getenv("SECURITY_PROTOCOL", "SSL"),
        api_version=(1, 0, 0),
    )

    topics = [{"name": "oanda_instrument", "partitions": 3, "replication": 3}]

    topic_list = list()

    for topic in topics:
        topic_list.append(
            NewTopic(
                name=topic["name"],
                num_partitions=topic["partitions"],
                replication_factor=topic["replication"],
            )
        )

    admin_client.create_topics(new_topics=topic_list, validate_only=False)


if __name__ == "__main__":
    main()
