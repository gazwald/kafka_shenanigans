#!/usr/bin/env python3
from kafka.admin import KafkaAdminClient, NewTopic

bootstrap_servers = [
    "b-1.oanda-test.8zyfgp.c4.kafka.ap-southeast-2.amazonaws.com:9092",
    "b-2.oanda-test.8zyfgp.c4.kafka.ap-southeast-2.amazonaws.com:9092",
]

admin_client = KafkaAdminClient(
    bootstrap_servers=bootstrap_servers, client_id="oanda-test-create-topic"
)

topic_list = [
    NewTopic(name="oanda-test-topic-aud_usd", num_partitions=2, replication_factor=2)
]
admin_client.create_topics(new_topics=topic_list, validate_only=False)
