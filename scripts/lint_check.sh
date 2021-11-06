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
echo
echo "+++ Checking Dockerfiles +++"
for dockerfile in $(find -type f -name Dockerfile ! -path "*cdk.out*"); do
  echo "+++ Checking $dockerfile +++"
  docker run --rm -i hadolint/hadolint < $dockerfile
  echo
done
