from django import template
from django.db.models import Q
from interface.models import Submission

__author__ = 'Faisal'

register = template.Library()

def processor_status():
    return {
        'finished_jobs': Submission.objects.filter(status=Submission.STATUS_COMPLETE).count(),
        'pending_jobs': Submission.objects.filter(Q(status=Submission.STATUS_PENDING)|Q(status=Submission.STATUS_INTERRUPTED)).count()
    }

register.inclusion_tag('templatetags/processor_status.html')(processor_status)