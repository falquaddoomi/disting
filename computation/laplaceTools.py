import itertools
import os
import subprocess
from compgraph_web.settings import COMPUTE_ALL_SUBMAT_RANKS
from computation import maximaTools

__author__ = 'Natalie'
import scipy
import numpy
from scipy import linalg
import sympy
import math
import sys
import networkx
# from sympy.core.sympify import sympify
from sympy.polys.domains import ZZ
# from sympy.polys.solvers import RawMatrix
# from sympy.polys.fields import vfield

#faster rref calculation!
def _iszero(x):
    """Returns True if x is zero."""
    return x.is_zero

def rrefMine(self, simplified=False, iszerofunc=_iszero,
         simplify=False):
    """
    Return reduced row-echelon form of matrix and indices of pivot vars.

    To simplify elements before finding nonzero pivots set simplify=True
    (to use the default SymPy simplify function) or pass a custom
    simplify function.

    >>> from sympy import Matrix
    >>> from sympy.abc import x
    >>> m = Matrix([[1, 2], [x, 1 - 1/x]])
    >>> m.rref()
    ([1, 0]
    [0, 1], [0, 1])
    """

    pivot, r = 0, self[:,:].as_mutable()        # pivot: index of next row to contain a pivot
    pivotlist = []                  # indices of pivot variables (non-free)
    for i in range(r.cols):
        #print "col: %s out of %s" % (i, r.cols)
        if pivot == r.rows:
            break
        if simplify:
            #print " col simplify"
            r[pivot,i] = sympy.sympify(r[pivot,i])
        if iszerofunc(r[pivot,i]):
            #print " col iszerofunc"
            for k in range(pivot, r.rows):
                #print "     internal col: %s out of %s" % (k, r.rows)
                if simplify and k > pivot:
                    #print "     simplifying: %s" % (r[k,i])
                    if k == 8 and i == 8:
                        r[k,i] = sympy.sympify(r[k,i])
                    else:
                        r[k,i] = sympy.sympify(r[k,i])
                if not iszerofunc(r[k,i]):
                    break
            if k == r.rows - 1 and iszerofunc(r[k,i]):
                continue
            r.row_swap(pivot,k)
        scale = r[pivot,i]
        #print "scale"

        r.row(pivot, lambda x, _: x/scale)
        #print "row pivoting first"

        for j in range(r.rows):
            #print " rows: %s out of %s" % (j, r.rows)
            if j == pivot:
                continue
            scale = r[j,i]
            r.row(j, lambda x, k: x - scale*r[pivot,k])
            #print " row pivoting internal"

        pivotlist.append(i)
        pivot += 1
    return self._new(r), pivotlist

# must ensure rank of q = rank of r = n
def calcQ(B, n, A):
    Q = B

    symA = makeSymMat(A)
    symB = makeSymMat(B)
    symQ = makeSymMat(Q)
    symQ = symB

    for i in range(1, n):
        symQ = symQ.row_join(symA**i * symB)

    rank = calcRank(symQ)
    return Q, rank

# must ensure rank of q = rank of r = n
def calcR(A, C, n):
    R = C
    symA = makeSymMat(A)
    symC = makeSymMat(C)
    symR = makeSymMat(R)
    symR = symC

    for i in range(1, n):
        temp = symC * symA**i
        symR = symR.col_join(temp)

    rank = calcRank(symR)
    
    return (symR, rank)

#make the matrix symbolic
def makeSymMat(mat):
    row, col = mat.shape
    M = sympy.Matrix(row, col, lambda i,j: sympy.Symbol('a_%d%d' % (i+1,j+1)) if mat.getA()[i][j] == 1 else 0)
    return M

#TF is returned as symbolic
#A, B, C are not expected to be symbolic
def calcTF(A, B, C, n):

    s = sympy.Symbol('s')
    I = sympy.eye(n) * s
    symA = makeSymMat(A)


    #sysMat = I - symA
    #sysMat = sysMat.inv()
    #print 'sysMat'
    #print sysMat
    charEqn = (I - symA).det()
    #print 'determinant'
    #print sympy.collect(sympy.expand(sympy.simplify(charEqn)), s, evaluate=False)
    myCharEqn = charEqn
    myTFNum = C * (I - symA).adjugate() * B

    #print 'My characteristic eqn'
    #print myCharEqn
    #print 'numerator'
    #print myTFNum

    alphaDicts = []
    betaDicts = []
    #print 'rows'
    for elem in myTFNum:
        #print elem

        #newEqn = sympy.simplify(sympy.expand(elem))
        #newEqn = sympy.ratsimp(newEqn)
        #tfFrac = sympy.fraction(newEqn)
        elem = sympy.expand(sympy.simplify(elem))

        #alphas are the denominator
        currDictAlpha = sympy.collect(myCharEqn, s, evaluate=False)
        if len(currDictAlpha) > 0:
            alphaDicts.append(currDictAlpha)

        #betas are the numerator
        currDictBeta = sympy.collect(elem, s, evaluate=False)
        if len(currDictBeta) > 0:
            betaDicts.append(currDictBeta)


    #print  'Transfer Function'
    #print myTF
    #print  'betas'
    #print betaDicts
    myBetas = betaDicts
    myAlphas = alphaDicts
    #print 'alphas'
    #print alphaDicts
    #print 'done'

    return(myTFNum, myCharEqn, myAlphas, myBetas)

#powers of s
def getOrderedKeys(myDict):
    s = sympy.Symbol('s')
    totNumKeys = len(myDict)
    orderedKeys = []
    currPow = 0
    #print len(myDict)
    while len(orderedKeys) != totNumKeys:
        if s**currPow in myDict:
            orderedKeys.append(currPow)
        currPow = currPow + 1

    return orderedKeys

#how many symbols do we need?
def getNumSym(in_mat):
    numSym = 0
    for i in in_mat:
        if i != 0:
            numSym = numSym + 1
    #print ('numSym', numSym)
    return numSym

def alphaBetaToTransfer(adjMat, alphas, betas):
    s = sympy.Symbol('s')
    subs = {}

    # iterate over the columns of the adjacency matrix
    for i, col in enumerate(adjMat.getA()):
        expr = sympy.S(0)
        i += 1
        # iterate over the elements in each column of the adjacency matrix
        # this is to build the replacement expression for what were once "output to env"s
        # but are now the turnover rates of each node
        for j, elem in enumerate(col):
            j += 1
            if elem != 0:
                expr += (-sympy.var('a_%d%d' % (j,i)))

        subs[sympy.var('a_%d%d' % (i,i))] = expr

    #print "*** VAR->EXPR SUBSTITUTIONS: "
    #print subs

    for pos in range(0, len(betas)):
        orderedKeysBeta = getOrderedKeys(betas[pos])
        for key in orderedKeysBeta:
            betas[pos][s**key] = sympy.simplify(sympy.expand(betas[pos][s**key].xreplace(subs)))

        #finished all the betas so add the alphas, but only once
        orderedKeysAlpha = getOrderedKeys(alphas[pos])
        for key in orderedKeysAlpha:
            alphas[pos][s**key] = sympy.simplify(sympy.expand(alphas[pos][s**key].xreplace(subs)))

    #print "*** NEW ALPHAS: "
    #print alphas
    #print "*** NEW BETAS: "
    #print betas

def makeJacobianMat(alphas, betas):
    M = sympy.eye(1)
    s = sympy.Symbol('s')

    #print 'making jacobian'
    #print alphas
    #print betas


    firstTime = True
    firstTimeAlpha = True
    #making the 1-dim column for the Jacobian
    for pos in range(0, len(betas)):
        orderedKeysBeta = getOrderedKeys(betas[pos])
        for key in orderedKeysBeta:
            if firstTime:
                M[0, 0] = betas[pos][s**key]
                firstTime = False
                firstBeta = True
            else:
                M2 = sympy.Matrix(1, 1, [betas[pos][s**key]])
                M = M.col_join(M2)

        #finished all the betas so add the alphas, but only once
        if firstTimeAlpha:
            firstTimeAlpha = False
            orderedKeysAlpha = getOrderedKeys(alphas[pos])
            for key in orderedKeysAlpha:
                if firstTime:
                    M[0, 0] = alphas[pos][s**key]
                    firstTime = False
                #elif key != 4:
                else:
                    M2 = sympy.Matrix(1, 1, [alphas[pos][s**key]])
                    M = M.col_join(M2)

    #print 'jacobian'
    #print M
    return M

def getSymbols(AdjMat, Alphas, Betas):
    s = sympy.Symbol('s')
    symbols = []

    #one outer for loop for both since we are iterating over transfer functions
    for pos in range(0, len(Betas)):
        orderedKeysBeta = getOrderedKeys(Betas[pos])
        for key in orderedKeysBeta:
            if Betas[pos][s**key] != 1:
                symbols.append(Betas[pos][s**key])

        #finished all the betas so add the alphas
        orderedKeysAlpha = getOrderedKeys(Alphas[pos])
        for key in orderedKeysAlpha:
            if Alphas[pos][s**key] != 1:
                symbols.append(Alphas[pos][s**key])
    return symbols

def calcJacobian(symbolAdjMat, Alphas, Betas):
    symbols = []

    myGraf = networkx.MultiDiGraph(symbolAdjMat)
    #print 'edges'
    #print list(myGraf.edges())

    jcount= 1
    icount= 1
    for i in symbolAdjMat.getA():
        jcount = 1
        for j in i:
            if j != 0:
                symbols.append(sympy.var('a_%d%d' % (jcount,icount)))
            jcount = jcount + 1
        icount = icount + 1

    #make the alphas and betas related to the turnover rate
    #this changes Alphas and Betas
    alphaBetaToTransfer(symbolAdjMat, Alphas, Betas)

    #now create the matrix to do the Jacobian on
    jacMat = makeJacobianMat(Alphas, Betas)
    #print 'Jacobian fully calculated'
    myJac = jacMat.jacobian(symbols)
    #print myJac

    #print 'Jabobian %d, %d' % (myJac.rows, myJac.cols)

    return myJac

def calcRank(in_mat):
    return maximaTools.getMatrixRank(in_mat)

#this makes a list of all the sets of rows we need to analyze
def kbits(n, k):
    result = []
    for i in range(2, k+1):
        for bits in itertools.combinations(range(n), i):
            result.append(bits)
    return result

def makeNewMat(listRows, in_mat):
    M = sympy.eye(1)
    firstTime = True
    for rowIndex in listRows:
        if firstTime:
            M = sympy.Matrix(1, in_mat.cols, in_mat[rowIndex:rowIndex+1,:])
            firstTime = False
        else:
            M2 = sympy.Matrix(1, in_mat.cols, in_mat[rowIndex:rowIndex+1,:])
            M = M.col_join(M2)

    return M


def reducedJacMat(in_mat):
    reducedMat = sympy.eye(1)
    #print in_mat.cols
    allZero = sympy.Matrix(1, in_mat.cols, [0]*in_mat.cols)
    firstTime = True
    for rowIndex in range(in_mat.rows):
        currMat = sympy.Matrix(1, in_mat.cols, in_mat[rowIndex:rowIndex+1,:])
        if currMat != allZero:
            if firstTime:
                reducedMat = currMat
                firstTime = False
            else:
                reducedMat = reducedMat.col_join(currMat)


    return reducedMat

def calculateOverallRanks(in_mat, allCombos):
    ranks = []
    
    for i, currCombo in enumerate(allCombos):
        #make the matrix
        newSubMat = makeNewMat(currCombo, in_mat)
        # myRawMat = RawMatrix(newSubMat.rows, newSubMat.cols, map(F.to_domain().convert, newSubMat))
        rank = calcRank(newSubMat)
        ranks.append(rank)

    return ranks

# ===============================================
# === tree-based rank calculations below
# ===============================================

def kbits_tree(n, k):
    already_genned = set()
    IDs = tuple(range(n))
    return [kbits_tree_sub(x, k-1, already_genned) for x in itertools.combinations(IDs, k) if x not in already_genned]

def kbits_tree_sub(IDs, k, already_genned):
    # keep track of matrices we've already generated
    already_genned.add(IDs)

    # end recursion if we're at the base case (a matrix with no meaningful children)
    if k < 2:
        return IDs, []

    # otherwise, keep producing children of the given matrix
    return IDs, [kbits_tree_sub(x, k-1, already_genned) for x in itertools.combinations(IDs, k) if x not in already_genned]

# borrowed from http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python

import collections
def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def countTreeNodes(toplist):
    return sum([countTreeNodesRecurse(i) for i in toplist])

def countTreeNodesRecurse(top):
    toprows, topkids = top
    return 1 + sum([countTreeNodesRecurse(i) for i in topkids])

def calcAllSubranks(in_mat, k):
    rowTree = kbits_tree(in_mat.rows, k)
    return list(flatten([calcChildRank(x, in_mat, False) for x in rowTree]))

def calcChildRank(top, in_mat, alreadyRanked):
    toprows, topkids = top

    # F = vfield("a_(1:%d)(1:%d)" % (len(toprows), in_mat.cols), ZZ)
    # F = vfield("a_(1:5)(1:5)", ZZ)

    if alreadyRanked and not COMPUTE_ALL_SUBMAT_RANKS:
        rank = len(toprows)
    else:
        newSubMat = makeNewMat(toprows, in_mat)
        # myRawMat = RawMatrix(newSubMat.rows, newSubMat.cols, map(F.to_domain().convert, newSubMat))
        # rank = calcRank(myRawMat)
        rank = maximaTools.getMatrixRank(newSubMat)
        alreadyRanked = (rank == len(toprows))

    return rank, [calcChildRank(x, in_mat, alreadyRanked) for x in topkids]
