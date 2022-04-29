import os

import v20

from lib.ssm import get_ssm


def set_up_context(
    hostname: str,
    application: str,
    port: int = 443,
    ssl: bool = True,
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
