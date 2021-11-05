#!/usr/bin/bash 

cd $(dirname $0)/..

echo "+++ Checking with Black +++"
black .
echo
echo "+++ Checking with iSort +++"
isort --extend-skip cdk.out .
