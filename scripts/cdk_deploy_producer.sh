#!/usr/bin/env bash
cd $(dirname $0)/..

source .venv/bin/activate

echo "+++ Deploying producer +++"
cd producer  && cdk deploy --require-approval never --app ./stack.py && cd ..
