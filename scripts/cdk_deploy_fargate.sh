#!/usr/bin/env bash
cd $(dirname $0)/..

source .venv/bin/activate

echo "+++ Deploying fargate cluster... +++"
cdk deploy --require-approval never --app ./fargate/stack.py
