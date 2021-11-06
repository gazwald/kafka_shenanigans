#!/usr/bin/env bash
cd $(dirname $0)/..

echo "+++ Deploying Glue Registry and Schemas +++"
cd glue && cdk deploy --require-approval never --app ./stack.py && cd ..
