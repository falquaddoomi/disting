#!/bin/bash

function postmsg() {
  echo ""
  echo "---"
  echo "Success! DISTING is now running in the background at http://localhost:5580."
  echo ""
  echo "Notes:"
  echo "- Use docker ps to see the list of docker processes that are running."
  echo "- Use docker stop <container name> to stop it, and docker rm <container name> to clean it up afterward."
  echo "- You can also stop and restart subprocesses via supervisord's admin page at http://localhost:9001"
  echo "  (the username and password are the ones from your .env file)"
  echo "---"
}

if [ ! -f .env ]; then
  echo "ERROR: you need to create a .env file containing at least the following:"
  echo "ADMIN_USER=yourname"
  echo "ADMIN_PASS=yourpass"
  exit -1
fi

docker build -t disting .
docker run -d --security-opt seccomp=unconfined -p 5580:5580 -p 9001:9001 -v $(pwd):/app --env-file=.env disting \
  && postmsg
