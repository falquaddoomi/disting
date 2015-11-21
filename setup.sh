#!/bin/bash

echo "*** DISTING requirements installer v0.1"

echo -e "\n=== STEP 1. Install system packages via apt-get"

sudo apt-get install rabbitmq-server
sudo apt-get install maxima
sudo apt-get install python python-dev python-pip
sudo apt-get install gfortran libopenblas-dev liblapack-dev
sudo apt-get install screen

sudo pip install virtualenv

echo -e "\n=== STEP 2. Create project-local virtualenv and install python packages into it"

virtualenv .venv
.venv/bin/pip install -r requirements.txt

echo -e "\nComplete!"
echo "Start the project via the launch.sh script, which will start the interface, workers, and MAXIMA daemon"
