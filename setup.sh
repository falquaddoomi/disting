#!/bin/bash

echo "*** DISTING requirements installer v0.1"

echo -e "\n=== STEP 1. Install system packages via apt-get"

# note that maxima 5.32.1-1 is only in trusty;
# the below line will add that to /etc/apt/sources.list
sudo add-apt-repository -u "deb http://ch.archive.ubuntu.com/ubuntu/ trusty universe"
sudo apt-get install rabbitmq-server maxima=5.32.1-1 python python-dev python-pip gfortran libopenblas-dev liblapack-dev screen

# note that we *never* want to upgrade maxima due to them introducing breaking changes in minor version changes
sudo apt-mark hold maxima

sudo pip install virtualenv

echo -e "\n=== STEP 2. Create project-local virtualenv and install python packages into it"

virtualenv .venv
.venv/bin/pip install -r requirements.txt

echo -e "\nComplete!"
echo "Start the project via the launch.sh script, which will start the interface, workers, and MAXIMA daemon"
