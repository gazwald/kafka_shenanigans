#!/usr/bin/env bash
cd $(dirname $0)/..

source .venv/bin/activate

echo "+++ Deploying Glue Registry and Schemas +++"
cd glue && cdk deploy --require-approval never --app ./stack.py && cd ..
