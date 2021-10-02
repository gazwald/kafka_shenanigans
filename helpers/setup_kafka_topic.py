#!/usr/bin/env python3
from typing import Dict

import boto3
import yaml

from kafka.admin import KafkaAdminClient, NewTopic


def load_config(path: str = "config.yml") -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
ssm = boto3.client("ssm", region_name=CONFIG["region"])
glue = boto3.client("glue", region_name=CONFIG["region"])
msk = boto3.client("kafka", region_name=CONFIG["region"])


def get_ssm(path: str) -> str:
    r = ssm.get_parameter(Name=path, WithDecryption=True)

    if "Parameter" in r.keys():
        return r["Parameter"]["Value"]


bootstrap_servers = msk.get_bootstrap_brokers(ClusterArn=get_ssm("kafka/cluster_arn"))

client_id = CONFIG["app_name"] + "-create-topic"

admin_client = KafkaAdminClient(
    bootstrap_servers=bootstrap_servers["BootstrapBrokerStringTls"],
    client_id=client_id,
    security_protocol=CONFIG["kafka"]["protocol"],
    api_version=(
        CONFIG["kafka"]["protocol_version"]["major"],
        CONFIG["kafka"]["protocol_version"]["minor"],
        CONFIG["kafka"]["protocol_version"]["patch"],
    ),
)

topic_list = [NewTopic(name=CONFIG["topic"], num_partitions=2, replication_factor=2)]
admin_client.create_topics(new_topics=topic_list, validate_only=False)
