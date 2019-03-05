#!/bin/bash

if [ ! -f .env ]; then
  echo "ERROR: you need to create a .env file containing at least the following:"
  echo "ADMIN_USER=yourname"
  echo "ADMIN_PASS=yourpass"
  exit -1
fi

docker build -t disting .
docker run --security-opt seccomp=unconfined -p 5580:5580 -p 9001:9001 -v $(pwd):/app --env-file=.env disting
