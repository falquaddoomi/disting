DISTING: model indistinguishability identifier
====

This project aims to provide a means to identify the family of compartment models that are indistinguishable from a given model, via both graph-theoretic and moment-invariant techniques. The project provides a website (implemented in the Django framework) which is used as an interface to the processing pipeline (implemented via Celery, a distributed task queue processor.) The task processor also relies on Maxima, a symbolic solving system, to perform some of the moment-invariant computations.

## How to install and run DISTING

Clone this repository to a location of your choice on the server. Once it's there, run the **setup.sh** script and it will install all the requisite packages.

Run the **launch.sh** script and it will start a screen session with four subscreens, described below:

- server, which is the webserver that handles the interface (running on port 5580 by default),
- processor, which is a daemon that processes incoming jobs,
- workers, a celery instance that processes small asynchronous incoming tasks (mostly matrix rank calculations),
- shell, a shell that's already activated in the disting virtualenv that you can use for management, if need be.

You can safely detach from the screen session at this point by invoking Ctrl-a, Ctrl-d.

## Project details

DISTING consists of three components:
1. a web interface that users connect to via their browser to add jobs to a job queue and view the results,
2. a processor that handles running jobs in the queue
3. a pool of worker processes that handle running computations asynchronously for each job

### Web Interface
The **web interrface** is implemented in a Python web framework called Django (https://www.djangoproject.com/). If you wish to work on the interface, it's recommended that you read the Django documentation, or at least follow the "getting started" tutorial on the site.

The majority of the site's implementation can be found in
https://github.com/falquaddoomi/disting/tree/master/interface

### Job Processor
The **processor** is implemented as a Django management command. When first started, it starts a number (3 by default) of MAXIMA daemons that the worker processes use to execute MAXIMA code (e.g. matrix rank calculations.)

After that, it polls a table in the Django database that contains jobs and filters out jobs that haven't been started yet. Once it has a list of jobs to run, it executes each job in turn by invoking computation.main.processInput() with the job's details. When the job processing is complete, it stores the result back to the job table and continues on to the next unfinished job. If an error occurs during processing, it marks the job as incomplete and saves the error text to the job, then continues to the next job. Once it has exhausted all available jobs, it waits until more jobs are available and repeats the above process for the new jobs.

The job processor's code can be found in https://github.com/falquaddoomi/disting/blob/master/interface/management/commands/processor.py

### Worker Pool

The **workers** are implemented via Celery (http://www.celeryproject.org/), a distributed task queue. The workers allow the job processor to execute multiple computations in parallel (that is, without having to wait for the result of the previous computation before starting the next one.) Celery manages starting the workers, distributing tasks across them, and returning the results to the job processor.

The definition of the workers can be found here:
https://github.com/falquaddoomi/disting/blob/master/computation/tasks.py
