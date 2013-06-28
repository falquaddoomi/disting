from celery.task import task
from computation import laplaceTools

__author__ = 'Faisal'

@task()
def testAdd(a, b):
    return a+b

@task()
def deal_with_matrix(in_mat):
    return in_mat


@task()
def processSingleTotalJacobian(myGraphModel, cand):
    #first get the simplified jacobian
    cand.Jac = laplaceTools.reducedJacMat(cand.Jac)
    #get the ranks
    cand.JacComboRanks = laplaceTools.calcAllSubranks(cand.Jac, myGraphModel.Rank)

    if myGraphModel.JacComboRanks == cand.JacComboRanks:
        print "PASSED"
        return cand