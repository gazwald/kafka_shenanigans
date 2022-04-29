#!/usr/bin/env python3
import os

from aws_cdk import App, Environment
from stacks.kafkaesque import KafkaesqueStack

app = App()
env = Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)
KafkaesqueStack(app, "kafkaesque", env=env)
app.synth()
