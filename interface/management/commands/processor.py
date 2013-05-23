from django.core.management.base import BaseCommand, CommandError
import time, traceback
import sys
import computation.main
from interface.models import Submission

class Command(BaseCommand):
    args = ''
    help = 'Iterates over the job queue and processes jobs intermittently'

    def handle(self, *args, **options):
        self.stdout.write('=== compgraph job processing daemon v0.1 ===')

        while True:
            # read in jobs forever
            jobs = Submission.objects.filter(status=Submission.STATUS_PENDING)

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