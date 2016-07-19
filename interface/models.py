from collections import OrderedDict
from datetime import datetime
import json
from dateutil import relativedelta
import django.utils.timezone
from django.contrib.auth.models import User
from django.db import models
import re

# Create your models here.
from django.forms import ModelForm, model_to_dict, Form
from django.template.defaultfilters import default

class Submission(models.Model):
    # store the user who submitted this request
    user = models.ForeignKey(User)

    # and the name of the request
    name = models.CharField(max_length=300)

    # and the data for the job
    A = models.CharField(max_length=300)
    B = models.CharField(max_length=300)
    C = models.CharField(max_length=300)
    Adj = models.CharField(max_length=300)
    n = models.IntegerField()
    r = models.IntegerField()
    m = models.IntegerField()

    # helper method for formatting the job for the processor function
    def makeInput(self):
        return """A = %(A)s
B = %(B)s
C = %(C)s
Adj = %(Adj)s
n = %(n)s
r = %(r)s
m = %(m)s""" % model_to_dict(self)

    # submission time
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    updated_on = models.DateTimeField(auto_now=True, editable=False)
    started_on = models.DateTimeField(blank=True, null=True, editable=False)
    ended_on = models.DateTimeField(blank=True, null=True, editable=False)

    # status field
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETE = 'complete'
    STATUS_ERROR = 'error'
    STATUS_INTERRUPTED = 'interrupted'
    STATUS_CANCELLING = 'cancelling'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETE, 'Completed'),
        (STATUS_ERROR, 'Error'),
        (STATUS_ERROR, 'Interrupted'),
        (STATUS_CANCELLING, 'Cancelling'),
        (STATUS_CANCELLED, 'Cancelled')
    )

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # field to store log of stdout while running
    log = models.TextField(blank=True, editable=False)
    # fields for results
    result = models.TextField(blank=True, editable=False)

    def interval(self):
        if self.started_on is None:
            return "(never started)"
        elif self.ended_on is None:
            end = django.utils.timezone.now()
        else:
            end = self.ended_on

        rd = relativedelta.relativedelta (end, self.started_on)
        return "%d:%02d:%02d.%d" % (rd.hours, rd.minutes, rd.seconds, rd.microseconds)

    def graphs(self):
        # we can only produce a gallery of graph data if there actually were results
        if self.result.strip() == "":
            return None

        results = OrderedDict()

        # find and the original graph (aka "model 0")
        # (NOTE: there's really no need for re.finditer since we're just getting one result,
        # but it handles the case where it's not present at all gracefully)
        orig_matches = re.finditer(r"(Original Model)[^\n]*\n(\[([ ]*\[[01. ]+\]\n?)+\])", self.result, re.MULTILINE|re.DOTALL)

        for m in orig_matches:
            results["Model 0"] = json.loads(m.group(2).replace(". ",",").replace(".]", "]").replace("\n", ", "))
            # note this breaks on the first result, since there should be just one original model
            break

        # parse out the rest of the graph data
        matches = re.finditer(r"(Model [0-9]+)[^\n]*\n(\[([ ]*\[[01. ]+\]\n?)+\])", self.result, re.MULTILINE|re.DOTALL)

        for m in matches:
            results[m.group(1)] = json.loads(m.group(2).replace(". ",",").replace(".]", "]").replace("\n", ", "))

        return results

    def __unicode__(self):
        return "%s (#%d)" % (self.name, self.id)

class SubmissionForm(ModelForm):
    class Meta:
        exclude = ('user', 'status', 'log', 'result', 'created_on', 'updated_on', 'started_on', 'ended_on')
        model = Submission

class SubmissionAltForm(ModelForm):
    class Meta:
        exclude = ('user', 'status', 'log', 'result', 'created_on', 'updated_on', 'started_on', 'ended_on')
        model = Submission
