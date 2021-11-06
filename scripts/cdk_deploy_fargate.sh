#!/usr/bin/env bash
cd $(dirname $0)/..

echo "+++ Deploying fargate cluster... +++"
cdk deploy --require-approval never --app ./fargate/stack.py
