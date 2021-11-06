#!/usr/bin/env bash
cd $(dirname $0)/..

source .venv/bin/activate

echo "+++ Deploying kafka cluster... +++"
cdk deploy --require-approval never --app ./kafka/stack.py
