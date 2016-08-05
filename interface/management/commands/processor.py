from datetime import datetime
import django.utils.timezone
from django.core.management.base import BaseCommand, CommandError
import time, traceback
import sys
from django.db.models import Q
from compgraph_web.settings import PYMAX_INSTANCES
import computation.main
from computation.tasks import processSingleTotalJacobian
from interface.glue.maxima_multiproxy import MaximaMultiProxyServer
from interface.glue.maxima_proxy import MaximaProxyServer
from interface.models import Submission
import atexit

class JobCancelledException(Exception):
    pass

def logger_notify(msg, job):
    """
    Prints job output to the screen as well as makes it available on the interface.
    Also checks the interface each time it's called
    :type job: Submission
    """

    # refresh, log to, and save the object
    # we refresh so we can detect if it's been cancelled
    job = Submission.objects.get(id=job.id)
    job.log += "%s\n" % msg
    job.save()

    if job.status == Submission.STATUS_CANCELLING:
        print "Job cancelled, quitting..."
        raise JobCancelledException

    print msg

class Command(BaseCommand):
    args = ''
    help = 'Iterates over the job queue and processes jobs intermittently'

    def on_exit(self):
        print '=== ENDING TASK PROCESSOR ==='
        Submission.objects.filter(status=Submission.STATUS_RUNNING).update(status=Submission.STATUS_INTERRUPTED)
        Submission.objects.filter(status=Submission.STATUS_CANCELLING).update(status=Submission.STATUS_CANCELLED)

        # if self.maxima_server:
        #     self.maxima_server.stop()

        for server in self.max_servers:
            server.stop()

    def handle(self, *args, **options):
        self.stdout.write('=== compgraph job processing daemon v0.1 ===')

        # mark running jobs as incomplete if we terminate abruptly
        # also be sure to kill the server if it started
        atexit.register(self.on_exit)

        # start up the maxima server
        self.stdout.write(" => starting maxima server...")

        # self.maxima_server = MaximaMultiProxyServer(instances=3)
        # self.maxima_server.start()
        #
        # # wait until the server's up and ready...
        # while not self.maxima_server.all_ready():
        #     continue

        # instead, let's try to start multiple copies of the same server
        self.max_servers = []
        for i in range(PYMAX_INSTANCES):
            newServer = MaximaProxyServer(client_port=8523+i)
            newServer.start()
            self.max_servers.append(newServer)

        while not all([server.maxima_server.ready for server in self.max_servers]):
            continue

        self.stdout.write(" => ...all maxima instances online")

        # and then start processing jobs
        try:
            while True:
                # read in jobs forever
                jobs = Submission.objects.filter(Q(status=Submission.STATUS_PENDING)|Q(status=Submission.STATUS_INTERRUPTED))

                for job in jobs:
                    self.stdout.write('Starting job %d...' % job.id)

                    # indicate that we're about to run this job
                    job.status = Submission.STATUS_RUNNING
                    job.started_on = django.utils.timezone.now()
                    job.ended_on = None
                    job.log = ''
                    job.result = ''
                    job.save()

                    # run the job
                    try:
                        start_time = datetime.now()
                        result = computation.main.processInput(job.makeInput(), notify=lambda x: logger_notify(x, job))
                        print "Run time: %s" % str(datetime.now() - start_time)
                        # indicate that we're done
                        job.ended_on = django.utils.timezone.now()
                        job.result = result
                        job.status = Submission.STATUS_COMPLETE
                    except JobCancelledException:
                        job.status = Submission.STATUS_CANCELLED
                    except Exception as ex:
                        # indicate that we failed :(
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        job.ended_on = django.utils.timezone.now()
                        job.result = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                        traceback.print_exc()
                        job.status = Submission.STATUS_ERROR
                    finally:
                        # no matter what, save the result
                        job.ended_on = django.utils.timezone.now()
                        job.save()

                    self.stdout.write('Executed "%s" with final status %s' % (job, job.status))

                    # and sleep after each so we don't peg the CPU
                    time.sleep(2)

                # also sleep when we're done processing our current queue
                time.sleep(2)
        except KeyboardInterrupt:
            print "Keyboard interrupt!"