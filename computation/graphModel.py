__author__ = 'Natalie'
import scipy
import numpy
from scipy import linalg
import sympy
import math
import sys
import networkx
import laplaceTools

def default_notify(msg):
    print msg

class graphModel(object):

    def __init__(self, A, B, C, n, r, m, AdjMat, notify=default_notify):
        self.A = A
        self.B = B
        self.C = C
        self.n = n
        self.r = r

        #max number of parameters
        self.m = m

        self.JacComboCode = None
        self.JacComboRanks = None

        self.AdjMat = AdjMat

        (self.Q, self.QRank) = laplaceTools.calcQ(self.B, self.n, self.A)
        notify(" => completed laplaceTools.calcQ")

        (self.R, self.RRank) = laplaceTools.calcR(self.A, self.C, self.n)
        notify(" => completed laplaceTools.calcR")

        #self.betas is a list of dictionaries
        #self.alphas is a dictionary of the alphas from the char eqn
        self.TF, self.CharEqn, self.Alphas, self.Betas = laplaceTools.calcTF(self.A, self.B, self.C, self.n)

        notify(" => completed laplaceTools.calcTF")
        #print "my TF: %s" % self.TF
        #print "my CharEqn: %s" % self.CharEqn
        #print "my Alphas: %s" % self.Alphas
        #print "my Betas: %s" % self.Betas


        currNum = 0
        self.alphaKeys = []
        for currDict in self.Alphas:
            self.alphaKeys.append(laplaceTools.getOrderedKeys(currDict))
            #print 'alphaKeys%d' % currNum
            #print laplaceTools.getOrderedKeys(currDict)
            currNum = currNum + 1

        currNum = 0
        self.betaKeys = []
        for currDict in self.Betas:
            self.betaKeys.append(laplaceTools.getOrderedKeys(currDict))
            #print 'betaKeys%d' % currNum
            #print laplaceTools.getOrderedKeys(currDict)
            currNum = currNum + 1

        notify(" => completed laplaceTools.getOrderedKeys")
        #need to fix this self.TF = only the numerator now, need to divide each elem by char eqn
        self.Jac = laplaceTools.calcJacobian(self.AdjMat, self.Alphas, self.Betas)
        notify(" => completed laplaceTools.calcJacobian")
        #print self.Jac
        self.Rank = laplaceTools.calcRank(self.Jac)
        notify(" => completed laplaceTools.calcRank")
        #print 'row of orig Jac: %d, col: %d' %(self.Jac.rows, self.Jac.cols)
        # self.Rank = 7
        #print "done calculating rank stuff"
        #print 'AdjMat'
        #print self.AdjMat
        self.myGraph = self.makeGraph(self.AdjMat)


    def makeGraph(self, AdjMat):
        AdjMat = numpy.matrix(AdjMat)
        myGraph = networkx.MultiDiGraph(AdjMat)
        return myGraph

