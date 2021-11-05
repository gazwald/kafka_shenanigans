#!/usr/bin/bash 

cd $(dirname $0)/..

echo "+++ Checking with Black +++"
black --check .
echo
echo "+++ Checking with iSort +++"
isort --check --extend-skip cdk.out .
echo
echo "+++ Checking with MyPy +++"
mypy .
