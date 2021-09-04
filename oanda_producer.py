#!/usr/bin/env python3
import boto3
import v20
import yaml

from enum import Enum
from typing import List, Dict


client = boto3.client("ssm")


class MessageType(str, Enum):
    heartbeat = 'pricing.PricingHeartbeat'
    price = 'pricing.ClientPrice'


def set_up_context(
    api_token: str,
    hostname: str = "stream-fxtrade.oanda.com",
    port: int = 443,
    ssl: bool = True,
    application: str = "oanda-test",
    datetime_format: str = "UNIX",
):
    ctx = v20.Context(
        hostname,
        port,
        ssl,
        application=application,
        token=api_token,
        datetime_format=datetime_format,
    )

    return ctx


def get_ssm(path: str) -> str:
    r = client.get_parameter(Name=path, WithDecryption=True)

    if "Parameter" in r.keys():
        return r["Parameter"]["Value"]


def main():
    instruments: List[str] = ['AUD_USD']
    api_token: str = get_ssm("/oanda/key")
    account_id: str = get_ssm("/oanda/account")
    ctx = set_up_context(api_token)
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
            print(message)


if __name__ == "__main__":
    main()
