#!/usr/bin/bash 

black $1
isort $1
mypy $1
