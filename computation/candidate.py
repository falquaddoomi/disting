__author__ = 'Natalie'
import scipy
import numpy
from scipy import linalg
import sympy
import math
import sys
import networkx
import laplaceTools

class candidate(object):

    def __init__(self, AdjMat):
        self.AdjMat = numpy.matrix(AdjMat)
        self.myGraph = networkx.MultiDiGraph(self.AdjMat)
        #self.A = scipy.mat(AdjMat).T
        self.A = numpy.matrix(AdjMat).T
        self.Alphas = None
        self.Betas = None
        self.JacComboRanks = None

        checkForOutputMat = self.A.T

        for rowIndex, row in enumerate(self.A.tolist()):
            for colIndex, col in enumerate(row):
                if rowIndex == colIndex:
                    #can also check for this later and checkForOutputMat[rowIndex].any() == 1
                    self.A[(rowIndex, colIndex)] = 1


        self.A = scipy.mat(self.A)

    def calcJacobianRank(self):
        self.Jac = laplaceTools.calcJacobian(self.AdjMat, self.Alphas, self.Betas)
        #self.Rank = laplaceTools.calcRank(self.Jac)
        self.Rank = laplaceTools.calcRank(self.Jac)


