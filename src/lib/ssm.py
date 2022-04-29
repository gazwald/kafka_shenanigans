import os

from boto3.session import Session
from mypy_boto3_ssm.client import SSMClient
from mypy_boto3_ssm.type_defs import GetParameterResultTypeDef

REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
ssm: SSMClient = Session().client("ssm", region_name=REGION)


def get_ssm(path: str, default: str = "") -> str:
    try:
        r: GetParameterResultTypeDef = ssm.get_parameter(Name=path, WithDecryption=True)
    except ssm.exceptions.ParameterNotFound:
        if default:
            return default
        else:
            raise
    else:
        return r.get("Parameter", {}).get("Value", "")

    return ""
