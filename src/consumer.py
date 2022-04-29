#!/usr/bin/env python3
import logging
import os
import sys
from typing import Any, Dict, Optional, Union

import avro.io
import avro.schema
import v20
from boto3.session import Session

from lib.context import set_up_context
from lib.enums import HostType
from lib.exceptions import SchemaNotActive
from lib.kafka import set_up_consumer
from lib.schema import get_schema, message_is_valid_for_schema
from lib.ssm import get_ssm

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
DEBUG: bool
if os.getenv("DEBUG", None):
    DEBUG = True
else:
    DEBUG = False

ACCOUNT_ID: str = get_ssm("/oanda/account")


def create_order(ctx, order):
    return ctx.order.market(ACCOUNT_ID, order)


def do_something_with_data(message):
    return None


def main():
    logging.info("Starting...")
    consumer = set_up_consumer()
    schema = get_schema()

    for message in consumer:
        if DEBUG:
            logging.info(message)
        ctx = set_up_context(HostType.api, os.getenv("APP_NAME", "oanda_consumer"))
        if message_is_valid_for_schema(schema, message):
            r = do_something_with_data(message)
            if r:
                create_order(ctx, r)

    logging.info("Ending.")


if __name__ == "__main__":
    main()
