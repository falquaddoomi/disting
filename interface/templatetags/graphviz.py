from django import template
from django.db.models import Q
from interface.models import Submission

__author__ = 'Faisal'

register = template.Library()

def native_to_lists(native):
    out = []
    rows = native.strip("[]").split(";")
    for row in rows:
        out.append([x.strip() for x in row.split(" ") if x.strip() != ""])
    return out

def minigraph(job, name, model):
    """
    Produces a small, interactive graph based on the given job and the found model.
    :type job: Submission
    """

    adjacencies = []

    # loop through candidate model adj matrix and determine all adjacencies
    for i in range(0, len(model)):
        for j in range(0, len(model[i])):
            if int(model[i][j]) == 1:
                adjacencies.append((j,i))

    # loop through job B and C mats to determine input and output nodes
    Blist = native_to_lists(job.B)
    Clist = native_to_lists(job.C)

    inputs = []
    outputs = []

    for i in range(0, len(Blist)):
        for j in range(0, len(Blist[i])):
            if int(Blist[i][j]) == 1:
                inputs.append(i)

    for i in range(0, len(Clist)):
        for j in range(0, len(Clist[i])):
            if int(Clist[i][j]) == 1:
                outputs.append(j)

    # iterate through the diagonals of the adjacency matrix to find leaks
    leaks = []

    for x in range(0, len(model)):
        if int(model[x][x]) == 1:
            leaks.append(x)

    # and finally build a full description

    ctx = {
        'job': job,
        'name': name,
        'model': model,
        'nodes': range(0, len(model)),
        'adjacencies': adjacencies,
        'inputs': inputs,
        'outputs': outputs,
        'leaks': leaks
    }
    return ctx

register.inclusion_tag('templatetags/minigraph.html')(minigraph)