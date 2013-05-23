# Create your views here.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from interface.models import SubmissionForm, Submission

@login_required
def home(request):
    # render the queue
    context = {
        'jobs': Submission.objects.filter(user=request.user),
        'pending': Submission.objects.filter(user=request.user,status=Submission.STATUS_PENDING),
        'running': Submission.objects.filter(user=request.user,status=Submission.STATUS_RUNNING),
        'completed': Submission.objects.filter(user=request.user,status=Submission.STATUS_COMPLETE),
    }
    return render_to_response("queue.html", context, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('interface:home')

@login_required
def addjob(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SubmissionForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form_model = form.save(commit=False)
            form_model.user = request.user
            form_model.save()
            return redirect('interface:home') # Redirect after POST
    else:
        form = SubmissionForm() # An unbound form

    return render_to_response("addjob.html", {'requestform': form}, context_instance=RequestContext(request))

def viewresults(request, jobID):
    context = {
        'job': Submission.objects.get(id=jobID),
    }
    return render_to_response("results.html", context, context_instance=RequestContext(request))

def resubmitjob(request, jobID):
    job = Submission.objects.get(user=request.user,id=jobID)
    job.status = Submission.STATUS_PENDING
    job.result = ''
    job.save()
    return redirect('interface:home')

def removejob(request, jobID):
    Submission.objects.get(user=request.user,id=jobID).delete()
    return redirect('interface:home')