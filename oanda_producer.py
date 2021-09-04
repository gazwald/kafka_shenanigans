#!/usr/bin/env python3
import boto3
import v20
import yaml

from enum import Enum
from typing import List, Dict

from kafka import KafkaProducer


class MessageType(str, Enum):
    heartbeat = "pricing.PricingHeartbeat"
    price = "pricing.ClientPrice"


def load_config(path: str = "config.yml") -> Dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
client = boto3.client("ssm", region_name=CONFIG["region"])


def get_ssm(path: str) -> str:
    r = client.get_parameter(Name=path, WithDecryption=True)

    if "Parameter" in r.keys():
        return r["Parameter"]["Value"]


def set_up_producer(
    bootstrap_servers: List[str] = CONFIG["bootstrap_servers"],
    client_id: str = CONFIG["app_name"],
):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        client_id=client_id,
        security_protocol="SSL",
        api_version=(1, 0, 0),
    )


def set_up_context(
    hostname: str = "stream-fxtrade.oanda.com",
    port: int = 443,
    ssl: bool = True,
    application: str = CONFIG["app_name"],
    datetime_format: str = "UNIX",
):
    api_token: str = get_ssm(CONFIG["api_token"])
    ctx = v20.Context(
        hostname,
        port,
        ssl,
        application=application,
        token=api_token,
        datetime_format=datetime_format,
    )

    return ctx


def main():
    producer = set_up_producer()
    instruments: List[str] = CONFIG["instruments"]
    account_id: str = get_ssm(CONFIG["account_id"])
    ctx = set_up_context()
    r = ctx.pricing.stream(
        account_id,
        snapshot=True,
        instruments=",".join(instruments),
    )

    for msg_type, msg in r.parts():
        try:
            if msg_type == MessageType.heartbeat:
                message = msg.dict()
            elif msg_type == MessageType.price:
                message = msg.dict()
            else:
                print(f"Received unknown message type: {msg_type}")
        except KeyboardInterrupt:
            break
        else:
            producer.send(CONFIG["topic"], message)


if __name__ == "__main__":
    main()
