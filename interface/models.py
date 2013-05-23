from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.forms import ModelForm, model_to_dict
from django.template.defaultfilters import default

class Submission(models.Model):
    # store the user who submitted this request
    user = models.ForeignKey(User)

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
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # status field
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETE = 'complete'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETE, 'Completed'),
        (STATUS_ERROR, 'Error')
    )

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # fields for results
    result = models.TextField()

class SubmissionForm(ModelForm):
    class Meta:
        exclude = ('user', 'status', 'result')
        model = Submission
