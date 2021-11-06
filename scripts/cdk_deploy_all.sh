#!/usr/bin/env bash
cd $(dirname $0)/..

./scripts/cdk_deploy_fargate.sh
./scripts/cdk_deploy_kafka.sh
./scripts/cdk_deploy_producer.sh
./scripts/cdk_deploy_consumers.sh
