#!/usr/bin/env bash
cd $(dirname $0)/..

source .venv/bin/activate

echo "+++ Deploying consumers +++"
cd consumers && cdk deploy --require-approval never --app ./stack.py && cd ..
