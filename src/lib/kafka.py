import os

from boto3.session import Session
from kafka import KafkaConsumer, KafkaProducer
from mypy_boto3_kafka.client import KafkaClient
from mypy_boto3_kafka.type_defs import GetBootstrapBrokersResponseTypeDef

from lib.ssm import get_ssm

REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
msk: KafkaClient = Session().client("kafka", region_name=REGION)


def set_up_consumer():
    topic = get_ssm("/oanda/kafka/topic", "oanda_instrument")
    try:
        bootstrap_servers: GetBootstrapBrokersResponseTypeDef = (
            msk.get_bootstrap_brokers(ClusterArn=get_ssm("/oanda/kafka/cluster_arn"))
        )
    except msk.exceptions.BadRequestException:
        return None
    else:
        return KafkaConsumer(
            topic,
            group_id=os.getenv("APP_NAME", "oanda_consumer"),
            bootstrap_servers=bootstrap_servers["BootstrapBrokerStringTls"],
            security_protocol=os.getenv("SECURITY_PROTOCOL", "SSL"),
            api_version=(1, 0, 0),
        )


def set_up_producer():
    try:
        bootstrap_servers: GetBootstrapBrokersResponseTypeDef = (
            msk.get_bootstrap_brokers(ClusterArn=get_ssm("/oanda/kafka/cluster_arn"))
        )
    except msk.exceptions.BadRequestException:
        return None
    else:
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers["BootstrapBrokerStringTls"],
            client_id=os.getenv("APP_NAME", "oanda_producer"),
            security_protocol=os.getenv("SECURITY_PROTOCOL", "SSL"),
            api_version=(1, 0, 0),
        )
