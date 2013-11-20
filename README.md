DISTING: model indistinguishability identifier
====

This project aims to provide a means to identify the family of compartment models that are indistinguishable from a given model, via both graph-theoretic and moment-invariant techniques. The project provides a website (implemented in the Django framework) which is used as an interface to the processing pipeline (implemented via Celery, a distributed task queue processor.) The task processor also relies on Maxima, a symbolic solving system, to perform some of the moment-invariant computations.

To run your own version of the site, you should do the following:

Pre-Step) Check out this project locally, preferably on a linux machine. For other platforms, getting the Django site to run shouldn't be too challenging, but Celery and Maxima will likely be another story...

1) Set up your build environment. On Ubuntu, the command to install the relevant packages is the following:

sudo apt-get install python python-pip rabbitmq-server maxima

2) In another directory (preferably one outside of your checkout directory), set up and populate your virtualenv, like so:

sudo pip install virtualenv
virtualenv disting_env
source disting_env/bin/activate
pip install -r ../path/to/checked-out-project/requirements.txt

3) Back in the checkout directory, open up server_screen and edit the sections mentioned in the comments within. Run the DISTING components using screen, which will set up a session from which you can monitor the various processes:

screen -S disting -c server_screen

At this point, you should have a screen session running with four subscreens:
- server, which is the webserver (running on port 5580 by default),
- processor, which is a daemon that processes incoming jobs,
- workers, a celery instance that processes small asynchronous incoming tasks (mostly matrix rank calculations),
- shell, a shell that's already activated in the disting virtualenv that you can use for management, if need be.
