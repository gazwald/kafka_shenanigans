#!/usr/bin/env python3
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import avro.io
import avro.schema
from boto3.session import Session

from lib.context import set_up_context
from lib.enums import HostType, MessageType
from lib.kafka import set_up_producer
from lib.schema import get_schema, message_is_valid_for_schema
from lib.ssm import get_ssm

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
DEBUG: bool
if os.getenv("DEBUG", None):
    DEBUG = True
else:
    DEBUG = False

ACCOUNT_ID: str = get_ssm("/oanda/account")


def main():
    logging.info("Starting...")
    producer = set_up_producer()
    topic = get_ssm("/oanda/kafka/topic", "oanda_instrument")
    schema = get_schema()

    if schema:
        instruments: List[str] = ["AUD_USD"]
        ctx = set_up_context(HostType.stream, os.getenv("APP_NAME", "oanda_producer"))
        r = ctx.pricing.stream(
            ACCOUNT_ID,
            snapshot=True,
            instruments=",".join(instruments),
        )

        for msg_type, msg in r.parts():
            if DEBUG:
                logging.info(msg)
            try:
                if msg_type == MessageType.heartbeat:
                    message = msg.dict()
                elif msg_type == MessageType.price:
                    message = msg.dict()
                else:
                    logging.info(f"Received unknown message type: {msg_type}")
            except KeyboardInterrupt:
                break
            else:
                if message_is_valid_for_schema(schema, message):
                    producer.send(topic, message)

    logging.info("Ending.")


if __name__ == "__main__":
    main()
