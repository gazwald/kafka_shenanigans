#!/usr/bin/env python3
import yaml
from typing import Dict
from kafka.admin import KafkaAdminClient, NewTopic


def load_config(path: str = "config.yml") -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
client_id = CONFIG["app_name"] + "-create-topic"

admin_client = KafkaAdminClient(
    bootstrap_servers=CONFIG["kafka"]["bootstrap_servers"],
    client_id=client_id,
    security_protocol=CONFIG['kafka']['protocol'],
    api_version=(
        CONFIG['kafka']['protocol_version']['major'],
        CONFIG['kafka']['protocol_version']['minor'],
        CONFIG['kafka']['protocol_version']['patch'],
    )
)

topic_list = [NewTopic(name=CONFIG["topic"], num_partitions=2, replication_factor=2)]
admin_client.create_topics(new_topics=topic_list, validate_only=False)
