from celery.task import task

__author__ = 'Faisal'

@task()
def testAdd(a, b):
    return a+b

@task
def deal_with_matrix(in_mat):
    return in_mat