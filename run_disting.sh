#!/bin/bash

if [ ! -f .env ]; then
  echo "ERROR: you need to create a .env file containing at least the following:"
  echo "ADMIN_USER=yourname"
  echo "ADMIN_USER=yourpass"
  exit -1
fi

docker build -t disting .
docker run -d --rm --security-opt seccomp=unconfined -v $(pwd):/app --env-file=.env disting
