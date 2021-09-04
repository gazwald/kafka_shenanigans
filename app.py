#!/usr/bin/env python3
import boto3
import v20

from typing import List


client = boto3.client("ssm")


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
        print(f"Type: {msg_type}, Message: {msg}")
        if msg_type == "pricing.Heartbeat":
            pass
        elif msg_type == "pricing.Price":
            pass


if __name__ == "__main__":
    main()
