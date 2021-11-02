#!/usr/bin/env python3
import os
from enum import Enum
from typing import Any, Dict, List, Optional

import avro.io
import avro.schema
import boto3
import v20
from kafka import KafkaConsumer


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


def set_up_consumer():
    msk = boto3.client("kafka", region_name=REGION)
    try:
        bootstrap_servers: Dict[str, Any] = msk.get_bootstrap_brokers(
            ClusterArn=get_ssm("/oanda/kafka/cluster_arn")
        )
    except msk.exceptions.BadRequestException:
        return None
    else:
        return KafkaProducer(
            bootstrap_servers=bootstrap_servers["BootstrapBrokerStringSaslIam"],
            client_id=os.getenv("APP_NAME", "oanda_consumer"),
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
    """
    TODO: This needs to be the trading API, not the Streaming API
    """
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
        application=os.getenv("APP_NAME", "oanda_consumer"),
        token=api_token,
        datetime_format=datetime_format,
    )

    return ctx


def main():
    consumer = set_up_consumer()
    topic = get_ssm("/oanda/kafka/topic", "instrument")
    schema = get_schema()

    # Make money

if __name__ == "__main__":
    main()
