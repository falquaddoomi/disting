from django.core.management.base import BaseCommand, CommandError
import time, traceback
import sys
from django.db.models import Q
import computation.main
from interface.glue.maxima_proxy import MaximaProxyServer
from interface.models import Submission
import atexit

class JobCancelledException(Exception):
    pass

class Command(BaseCommand):
    args = ''
    help = 'Iterates over the job queue and processes jobs intermittently'

    def on_exit(self):
        print '=== ENDING TASK PROCESSOR ==='
        Submission.objects.filter(status=Submission.STATUS_RUNNING).update(status=Submission.STATUS_INTERRUPTED)
        if self.maxima_server:
            self.maxima_server.stop()

    def handle(self, *args, **options):
        self.stdout.write('=== compgraph job processing daemon v0.1 ===')

        # mark running jobs as incomplete if we terminate abruptly
        # also be sure to kill the server if it started
        atexit.register(self.on_exit)

        # start up the maxima server
        self.stdout.write(" => starting maxima server...")

        self.maxima_server = MaximaProxyServer()
        self.maxima_server.start()

        # wait until the server's up and ready...
        while not self.maxima_server.maxima_server.ready:
            continue

        # and then start processing jobs
        try:
            while True:
                # read in jobs forever
                jobs = Submission.objects.filter(Q(status=Submission.STATUS_PENDING)|Q(status=Submission.STATUS_INTERRUPTED))

                for job in jobs:
                    self.stdout.write('Starting job %d...' % job.id)

                    # indicate that we're about to run this job
                    job.status = Submission.STATUS_RUNNING
                    job.save()

                    # run the job
                    try:
                        result = computation.main.processInput(job.makeInput())
                        # indicate that we're done
                        job.result = result
                        job.status = Submission.STATUS_COMPLETE
                    except Exception as ex:
                        # indicate that we failed :(
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        job.result = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                        traceback.print_exc()
                        job.status = Submission.STATUS_ERROR

                    # either way, save the result
                    job.save()

                    self.stdout.write('Executed "%s" with final status %s' % (job, job.status))

                    # and sleep after each so we don't peg the CPU
                    time.sleep(2)

                # also sleep when we're done processing our current queue
                time.sleep(2)
        except KeyboardInterrupt:
            print "Keyboard interrupt!"