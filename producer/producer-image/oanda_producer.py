#!/usr/bin/env python3
import os
from enum import Enum
from typing import Any, Dict, List, Optional

import avro.io
import avro.schema
import boto3
import v20

from kafka import KafkaProducer


class MessageType(str, Enum):
    heartbeat: str = "pricing.PricingHeartbeat"
    price: str = "pricing.ClientPrice"


class SchemaNotActive(Exception):
    """Schema not marked ACTIVE in Registry"""

    pass


REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
ssm = boto3.client("ssm", region_name=REGION)


def get_ssm(path: str, default: Optional[str] = "") -> str:
    try:
        r: Dict[str, Any] = ssm.get_parameter(Name=path, WithDecryption=True)
    except ssm.exceptions.ParameterNotFound:
        if default:
            return default
        else:
            pass
    else:
        if "Parameter" in r.keys():
            return r["Parameter"]["Value"]

    return ""


def set_up_producer():
    msk = boto3.client("kafka", region_name=REGION)
    try:
        bootstrap_servers: Dict[str, Any] = msk.get_bootstrap_brokers(
            ClusterArn=get_ssm("/oanda/kafka/cluster_arn")
        )
    except msk.exceptions.BadRequestException:
        return None
    else:
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers["BootstrapBrokerString"],
            client_id=os.getenv("APP_NAME", "oanda_producer"),
            security_protocol=os.getenv("SECURITY_PROTOCOL", "SSL"),
            api_version=(1, 0, 0),
        )


def get_schema():
    glue = boto3.client("glue", region_name=REGION)
    version: str = os.getenv("SCHEMA_VERSION", "")
    if version:
        version_number: Dict[str, int] = {"VersionNumber": int(version)}
    else:
        version_number: Dict[str, bool] = {"LatestVersion": True}

    schema: Dict[str, Any] = glue.get_schema_version(
        SchemaId={
            "RegistryName": os.getenv("SCHEMA_REGISTRY", "oanda"),
            "SchemaName": os.getenv("SCHEMA_NAME", "instrument"),
        },
        SchemaVersionNumber=version_number,
    )

    if schema["Status"] == "AVAILABLE":
        s = avro.schema.parse(schema["SchemaDefinition"])
        return s
    else:
        raise SchemaNotActive


def set_up_context(
    hostname: str = "stream-fxtrade.oanda.com",
    port: int = 443,
    ssl: bool = True,
    datetime_format: str = "UNIX",
):
    api_token: str = get_ssm("/oanda/key")
    ctx = v20.Context(
        hostname,
        port,
        ssl,
        application=os.getenv("APP_NAME", "oanda_producer"),
        token=api_token,
        datetime_format=datetime_format,
    )

    return ctx


def main(send_to_kafka: bool = False):
    producer = set_up_producer()
    topic = get_ssm("/oanda/kafka/topic", "oanda_instrument")
    schema = get_schema()

    if schema:
        instruments: List[str] = ["AUD_USD"]
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
                if avro.io.validate(schema, message):
                    if send_to_kafka:
                        producer.send(topic, message)
                    else:
                        print(message)
                else:
                    print(f"Recieved message did not parse validation: {message}")


if __name__ == "__main__":
    main()
