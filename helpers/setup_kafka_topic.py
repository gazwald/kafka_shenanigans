#!/usr/bin/env python3
import os
from typing import Any, Dict

import boto3

from kafka.admin import KafkaAdminClient, NewTopic

ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))
glue = boto3.client("glue", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))
msk = boto3.client("kafka", region_name=os.getenv("AWS_REGION", "ap-southeast-2"))


def get_ssm(path: str) -> str:
    r = ssm.get_parameter(Name=path, WithDecryption=True)

    if "Parameter" in r.keys():
        return r["Parameter"]["Value"]

    return ""


def main():
    bootstrap_servers: Dict[str, Any] = msk.get_bootstrap_brokers(
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
