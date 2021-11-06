#!/usr/bin/env bash
cd $(dirname $0)/..

echo "+++ Deploying consumers +++"
cd consumers && cdk deploy --require-approval never --app ./stack.py && cd ..
