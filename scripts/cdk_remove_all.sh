#!/usr/bin/env bash
cd $(dirname $0)/..

cdk destroy --require-approval never --app ./fargate/stack.py
cdk destroy --require-approval never --app ./kafka/stack.py
cd producer  && cdk destroy --require-approval never --app ./stack.py && cd ..
cd consumers && cdk destroy --require-approval never --app ./stack.py && cd ..
cd glue      && cdk destroy --require-approval never --app ./stack.py && cd ..
