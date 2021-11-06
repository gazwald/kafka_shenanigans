#!/usr/bin/env bash
cd $(dirname $0)/..

cd consumers && cdk destroy --require-approval never --app ./stack.py && cd ..
cd producer  && cdk destroy --require-approval never --app ./stack.py && cd ..
cd glue      && cdk destroy --require-approval never --app ./stack.py && cd ..

cdk destroy --require-approval never --app ./fargate/stack.py & 
cdk destroy --require-approval never --app ./kafka/stack.py &

wait
