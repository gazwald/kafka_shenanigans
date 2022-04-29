import logging
import os
import sys
from typing import Dict

import avro.schema
from boto3.session import Session
from mypy_boto3_glue.client import GlueClient
from mypy_boto3_glue.type_defs import (
    GetSchemaVersionResponseTypeDef,
    SchemaVersionNumberTypeDef,
)

from lib.exceptions import SchemaNotActive

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
SCHEMA_VERSION: str = os.getenv("SCHEMA_VERSION", "")
SCHEMA_REGISTRY: str = os.getenv("SCHEMA_REGISTRY", "oanda")
SCHEMA_NAME: str = os.getenv("SCHEMA_NAME", "instrument")

glue: GlueClient = Session().client("glue", region_name=REGION)


def get_schema() -> avro.schema:
    version_number: SchemaVersionNumberTypeDef
    if SCHEMA_VERSION:
        version_number = {"VersionNumber": int(SCHEMA_VERSION)}
    else:
        version_number = {"LatestVersion": True}

    schema: GetSchemaVersionResponseTypeDef = glue.get_schema_version(
        SchemaId={
            "RegistryName": SCHEMA_REGISTRY,
            "SchemaName": SCHEMA_NAME,
        },
        SchemaVersionNumber=version_number,
    )

    if schema["Status"] == "AVAILABLE":
        return parse_schema(schema)
    else:
        raise SchemaNotActive


def parse_schema(schema) -> avro.schema:
    return avro.schema.parse(schema["SchemaDefinition"])


def message_is_valid_for_schema(schema: avro.schema, message: Dict) -> bool:
    if avro.io.validate(schema, message):
        return True
    else:
        logging.info(f"Recieved message did not parse validation: {message}")

    return False
