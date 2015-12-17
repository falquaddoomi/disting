# Create your views here.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from interface.glue.sparsemats import Sparse2DMat
from interface.models import SubmissionForm, Submission


def home(request):
    return render_to_response("home.html", {}, context_instance=RequestContext(request))

@login_required
def queue(request):
    # render the queue
    context = {
        'jobs': Submission.objects.filter(user=request.user),
        'pending': Submission.objects.filter(user=request.user, status=Submission.STATUS_PENDING),
        'running': Submission.objects.filter(user=request.user, status=Submission.STATUS_RUNNING),
        'completed': Submission.objects.filter(user=request.user, status=Submission.STATUS_COMPLETE),
    }
    return render_to_response("queue.html", context, context_instance=RequestContext(request))


def logout_view(request):
    logout(request)
    return redirect('interface:home')

# ==============================================================
# === job adding/editing views
# ==============================================================

@login_required
def addjob(request):
    context = {}

    if request.method == 'POST': # If the form has been submitted...
        try:
            if 'job_name' not in request.POST or request.POST['job_name'].strip() == "":
                raise ValueError("Name required when creating a job")

            instance = Submission(
                user=request.user,
                name=request.POST['job_name']
            )

            Adjmat = Sparse2DMat(rows=request.POST['nodecount'], cols=request.POST['nodecount'])
            Amat = Sparse2DMat(rows=request.POST['nodecount'], cols=request.POST['nodecount'])
            Bmat = Sparse2DMat(rows=request.POST['nodecount'])
            Cmat = Sparse2DMat(cols=request.POST['nodecount'])

            # NOTE: added the -1's on the to's and fr's below
            # because they're now 1-indexed versus 0-indexed in the interface

            for k, v in request.POST.items():
                if str(k).startswith("item_"):
                    to, fr = (str(k).split("_"))[1].split("-")
                    Adjmat[int(to)-1, int(fr)-1] = 1
                elif str(k).startswith("input_"):
                    fr = (str(k).split("_"))[1]
                    Bmat[int(fr)-1, 0] = 1
                elif str(k).startswith("output_"):
                    fr = (str(k).split("_"))[1]
                    Cmat[0, int(fr)-1] = 1

            # transform the adjacency matrix into the A matrix
            for i in range(0, Amat.rows):
                for j in range(0, Amat.cols):
                    Amat[i,j] = Adjmat[i,j]

                    if i == j:
                        # fill this one in if there's any 1's on either the cols or rows of Adjmat
                        Amat[i,j] = 1 if any(Adjmat.row(i)) or any(Adjmat.col(j)) else 0

            # create the instance data from these matrices
            instance.A = str(Amat.tonative())
            instance.B = str(Bmat.tonative())
            instance.C = str(Cmat.tonative())
            instance.Adj = str(Adjmat.tonative())

            instance.n = request.POST['nodecount']
            instance.r = Bmat.cols
            instance.m = Cmat.rows

            # everything went ok; push the new model instance to the db and continue
            instance.save()
            return redirect('interface:queue') # Redirect after POST
        except Exception as ex:
            context['error'] = ex.message

    return render_to_response("addjob.html", context, context_instance=RequestContext(request))


@login_required
def editjob(request, jobID):
    # look up the job we're editing
    job = Submission.objects.get(id=jobID)

    context = {
        'job': job
    }

    if request.method == 'POST': # If the form has been submitted...
        try:
            if 'job_name' not in request.POST or request.POST['job_name'].strip() == "":
                raise ValueError("Name required when editing a job")

            job.name = request.POST['job_name']

            Adjmat = Sparse2DMat(rows=request.POST['nodecount'], cols=request.POST['nodecount'])
            Amat = Sparse2DMat(rows=request.POST['nodecount'], cols=request.POST['nodecount'])
            Bmat = Sparse2DMat(rows=request.POST['nodecount'], cols=1, default="0")
            Cmat = Sparse2DMat(cols=request.POST['nodecount'], rows=1, default="0")

            # NOTE: added the -1's on the to's and fr's below
            # because they're now 1-indexed versus 0-indexed in the interface

            for k, v in request.POST.items():
                if str(k).startswith("item_"):
                    to, fr = (str(k).split("_"))[1].split("-")
                    Adjmat[int(to)-1, int(fr)-1] = 1
                elif str(k).startswith("input_"):
                    fr = (str(k).split("_"))[1]
                    Bmat[int(fr)-1, 0] = 1
                elif str(k).startswith("output_"):
                    fr = (str(k).split("_"))[1]
                    Cmat[0, int(fr)-1] = 1

            # transform the adjacency matrix into the A matrix
            for i in range(0, Amat.rows):
                for j in range(0, Amat.cols):
                    Amat[i,j] = Adjmat[i,j]

                    if i == j:
                        # fill this one in if there's any 1's on either the cols or rows of Adjmat
                        Amat[i,j] = 1 if any(Adjmat.row(i)) or any(Adjmat.col(j)) else 0

            # create the instance data from these matrices
            job.A = str(Amat.tonative())
            job.B = str(Bmat.tonative())
            job.C = str(Cmat.tonative())
            job.Adj = str(Adjmat.tonative())

            job.n = request.POST['nodecount']
            job.r = Bmat.cols
            job.m = Cmat.rows

            # everything went ok; push the new model instance to the db and continue
            job.save()
            return redirect('interface:viewjob', jobID=job.id) # Redirect after POST
        except Exception as ex:
            context['error'] = ex.message

    return render_to_response("editjob.html", context, context_instance=RequestContext(request))

# -------------------
# --- alternate add/edit implementation...
# -------------------

# @login_required
# def addjob_alt(request):
#     if request.method == 'POST': # If the form has been submitted...
#         form = SubmissionForm(request.POST) # A form bound to the POST data
#         if form.is_valid(): # All validation rules pass
#             form_model = form.save(commit=False)
#             form_model.user = request.user
#             form_model.save()
#             return redirect('interface:queue') # Redirect after POST
#     else:
#         form = SubmissionForm() # An unbound form
#
#     return render_to_response("addjob_direct.html", {'requestform': form}, context_instance=RequestContext(request))

# @login_required
# def editjob_alt(request, jobID):
#     # look up the job we're editing
#     job = Submission.objects.get(id=jobID)
#
#     if request.method == 'POST': # If the form has been submitted...
#         form = SubmissionForm(request.POST, instance=job) # A form bound to the POST data
#         if form.is_valid(): # All validation rules pass
#             form_model = form.save(commit=False)
#             form_model.user = request.user
#             form_model.save()
#             return redirect('interface:queue') # Redirect after POST
#     else:
#         form = SubmissionForm(instance=job) # a form bound to existing data
#
#     context = {
#         'requestform': form,
#         'job': job
#     }
#
#     return render_to_response("editjob_direct.html", context, context_instance=RequestContext(request))

# ==============================================================
# === job result views
# ==============================================================

@login_required
def viewresults(request, jobID):
    job = Submission.objects.get(id=jobID)

    try:
        paginator = Paginator(job.graphs().items(), 18) # show 21 graphs per page

        # enable the paginator
        page = request.GET.get('page')
        try:
            jobgraphs_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            jobgraphs_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            jobgraphs_page = paginator.page(paginator.num_pages)

    except AttributeError:
        # we don't have any items, i guess; just return an empty set for now
        jobgraphs_page = []

    context = {
        'job': job,
        'jobgraph_items': jobgraphs_page
    }
    return render_to_response("results.html", context, context_instance=RequestContext(request))

# ==============================================================
# === job manipulation views
# ==============================================================

@login_required
def resubmitjob(request, jobID):
    job = Submission.objects.get(user=request.user, id=jobID)
    job.status = Submission.STATUS_PENDING
    job.result = ''
    job.save()
    return redirect('interface:queue')


@login_required
def removejob(request, jobID):
    Submission.objects.get(user=request.user, id=jobID).delete()
    return redirect('interface:queue')


@login_required
def canceljob(request, jobID):
    job = Submission.objects.get(user=request.user, id=jobID)

    if job.status != Submission.STATUS_RUNNING:
        job.status = Submission.STATUS_CANCELLED
    else:
        job.status = Submission.STATUS_CANCELLING

    job.result = 'cancelled'
    job.save()
    return redirect('interface:queue')
