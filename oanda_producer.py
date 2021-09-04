#!/usr/bin/env python3
import boto3
import v20

from enum import Enum
from typing import List

from kafka import KafkaProducer

client = boto3.client("ssm")
APPLICATION_NAME = 'oanda-test'


class MessageType(str, Enum):
    heartbeat = 'pricing.PricingHeartbeat'
    price = 'pricing.ClientPrice'


def get_ssm(path: str) -> str:
    r = client.get_parameter(Name=path, WithDecryption=True)

    if "Parameter" in r.keys():
        return r["Parameter"]["Value"]


def set_up_producer(bootstrap: List[str], client_id: str = APPLICATION_NAME):
    return KafkaProducer(bootstrap_servers=bootstrap, client_id=client_id)


def set_up_context(
    hostname: str = "stream-fxtrade.oanda.com",
    port: int = 443,
    ssl: bool = True,
    application: str = APPLICATION_NAME,
    datetime_format: str = "UNIX",
):
    api_token: str = get_ssm("/oanda/key")
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
    instruments: List[str] = ['AUD_USD']
    account_id: str = get_ssm("/oanda/account")
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
            producer.send('oanda-test-topic-aud_usd', message)


if __name__ == "__main__":
    bootstrap_servers: List[str] = [
        'b-1.oanda-test.8zyfgp.c4.kafka.ap-southeast-2.amazonaws.com:9092',
        'b-2.oanda-test.8zyfgp.c4.kafka.ap-southeast-2.amazonaws.com:9092'
    ]
    producer = set_up_producer(bootstrap_servers)
    main()
