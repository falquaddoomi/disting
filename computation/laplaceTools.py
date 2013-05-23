import itertools
import os
import subprocess

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
from sympy.polys.solvers import RawMatrix
from sympy.polys.fields import vfield

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

    #rankFile = open("ranks.nb", "w+")

    #print 'calculating the RREF'
    #rankFile.write('myA = {')
    #for rowIndex in range(n):
    #    if rowIndex == n-1:
    #        rankFile.write(str(symQ[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","}").replace("_",""))
    #    else:
    #        rankFile.write(str(symQ[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","},").replace("_",""))
    #rankFile.write('};')
    #rankFile.write('rank = MatrixRank[myA];')
    #rankFile.write('Export["ranks.txt",rank];')
    #rankFile.write('Exit[];')
    #rankFile.close()

    #subprocess.call(["MathKernel","-noprompt","-initfile","ranks.nb"])
    #f = open("ranks.txt", 'r')
    #rank = int(f.readlines()[0])
    #print rank

    #(row_reduced, pivots) = rrefMine(symQ, simplify=True)
    
    #rank = len(pivots)

    rank = calcRank(symQ)
    return (Q, rank)

# must ensure rank of q = rank of r = n
def calcR(A, C, n):
    R = C
    symA = makeSymMat(A)
    symC = makeSymMat(C)
    symR = makeSymMat(R)
    symR = symC

    #print n

    for i in range(1, n):
        temp = symC * symA**i
        symR = symR.col_join(temp)




    #rankFile = open("ranks.nb", "w+")

    #print 'calculating the RREF'
    #rankFile.write('myA = {')
    #for rowIndex in range(n):
    #    if rowIndex == n-1:
    #        rankFile.write(str(symR[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","}").replace("_",""))
    #    else:
    #        rankFile.write(str(symR[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","},").replace("_",""))
    #rankFile.write('};')
    #rankFile.write('rank = MatrixRank[myA];')
    #rankFile.write('Export["ranks.txt",rank];')
    #rankFile.write('Exit[];')
    #rankFile.close()

    #subprocess.call(["MathKernel","-noprompt","-initfile","ranks.nb"])
    #f = open("ranks.txt", 'r')
    #rank = int(f.readlines()[0])

    #(row_reduced, pivots) = rrefMine(symR, simplify=True)
    #rank = len(pivots)

    rank = calcRank(symR)
    
    return (symR, rank)

#make the matrix symbolic
def makeSymMat(mat):
    row, col = mat.shape
    M = sympy.Matrix(row, col, lambda i,j: sympy.Symbol('a_%d%d' % (i+1,j+1)) if mat.getA()[i][j] == 1 else 0)
    return M

def makeFieldMat(mat):
    row, col = mat.shape
    M = RawMatrix(row, col, lambda i,j: vfield("a_%d%d" % (i+1,j+1), ZZ) if mat.getA()[i][j] == 1 else 0)
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

from sympy import S
def calcAltRank(in_mat):
    n = in_mat.rows
    m = in_mat.cols

    
    F = vfield("a_(1:5)(1:5)", ZZ)

    myRawMat = RawMatrix(in_mat.rows, in_mat.cols, map(F.to_domain().convert, in_mat))
    
    (row_reduced, pivots) = myRawMat.rref(iszerofunc=lambda x: not x, simplify=lambda x: x)
    
    rank = len(pivots)
    
    return rank

def calcAltRankMini(in_mat):
    
    (row_reduced, pivots) = in_mat.rref(iszerofunc=lambda x: not x, simplify=lambda x: x)
    
    rank = len(pivots)
    
    return rank

#play with this for COLUMNS!!!
def calcRank2(in_mat):
    #print 'started calculating the rank'
    in_mat = in_mat
    n = in_mat.rows
    m = in_mat.cols

    #print in_mat
    #print 'rows: %d, cols %d' % (n, m)
    #non transpose rank, row reduced
    rank = n

    rankFile = open("ranks.nb", "w+")

    #print 'calculating the RREF'
    rankFile.write('myA = {')
    for rowIndex in range(n):
        if rowIndex == n-1:
            rankFile.write(str(in_mat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","}").replace("_",""))
        else:
            rankFile.write(str(in_mat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","},").replace("_",""))
    rankFile.write('};')
    rankFile.write('rank = MatrixRank[myA];')
    rankFile.write('Export["ranks.txt",rank];')
    rankFile.write('Exit[];')
    rankFile.close()

    subprocess.call(["MathKernel","-noprompt","-initfile","ranks.nb"])
    f = open("ranks.txt", 'r')
    rank = int(f.readlines()[0])
    #print "RESULTS: %d" % rank

    # (row_reduced, pivots) = in_mat.rref(simplify=False)
    # rank = len(pivots)
    #row_reduced = in_mat.rref(simplify=True)[0]
    #pivots = in_mat.rref(simplify=True)[1]
    #print 'row reduced'
    #print row_reduced
    #print 'row pivots'
    #print pivots

    #for i in range(row_reduced.rows):
    #    if sympy.Matrix(row_reduced[i*m:(i+1)*m]).norm() == 0:
    #        rank -= 1


    return rank

def calcRank(in_mat):
    in_mat = in_mat
    n = in_mat.rows
    m = in_mat.cols

    in_mat.expand()
    in_mat.simplify()
    in_mat.expand()

    #for rowIndex in range(n):
    #    if rowIndex == n-1:
    #        print(str(in_mat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","}").replace("_",""))
    #    else:
    #        print(str(in_mat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","},").replace("_",""))

    #(row_reduced, pivots) = in_mat.rref(simplify=True)
    #rank = len(pivots)
    #print 'my row rank'
    #print rank


    rank2 = calcAltRank(in_mat)
    #print 'mat rank'
    #print rank2

    return rank2

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




import time
def compareOverallRank(in_mat, maxLen, allCombos):

    n = in_mat.rows
    m = in_mat.cols


    #this makes a list of all the rows I need to get
    #allCombos = kbits(n, maxLen)

    #print 'All Combos'
    #print allCombos
    #print 'Orig Matrix'
    #for rowIndex in range(n):
    #    print in_mat[rowIndex:rowIndex+1,:]

    #now write the file
    ranks = []
    #rankFile = open("rankCombo.nb", "w+", buffering=1024)
    
    print '###########################----------------compareOverallRank---------------###############################'
    totalLen = len(allCombos)
    currPos = 0
    
    F = vfield("a_(1:5)(1:5)", ZZ)
    
    for i, currCombo in enumerate(allCombos):
        currPos+=1
        print '%d out of %d' % (currPos, totalLen)

        #make the matrix
        newSubMat = makeNewMat(currCombo, in_mat)
        n = newSubMat.rows
        m = newSubMat.cols
        

        myRawMat = RawMatrix(newSubMat.rows, newSubMat.cols, map(F.to_domain().convert, newSubMat))

        #(row_reduced, pivots) = rrefMine(newSubMat, simplify=True)
        
        start = time.time()
        rank = calcAltRankMini(myRawMat)

        end = time.time()-start
        if end > 10:
            print myRawMat
            print ('it took:', end)
            
        ranks.append(rank)

        #rankFile.write('myA%d = {' % i)
        #for rowIndex in range(n):
        #    if rowIndex == n-1:
        #        rankFile.write(str(newSubMat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","}").replace("_",""))
        #    else:
        #        rankFile.write(str(newSubMat[rowIndex:rowIndex+1,:]).replace("[","{").replace("]","},").replace("_",""))
        #rankFile.write('};')
        #rankFile.write('rank%d = MatrixRank[myA%d];' % (i, i))

    #now write the code to summarize the output
    #rankFile.write('totRanks = {')
    #for i, currCombo in enumerate(allCombos):
    #    if i == len(allCombos) - 1:
    #        rankFile.write('rank%d' % i)
    #    else:
    #        rankFile.write('rank%d,'% i)

    #rankFile.write('};')

    #rankFile.write('Export["rankCombo.txt",totRanks];')
    #rankFile.write('Exit[];')
    #rankFile.close()

    #subprocess.call(["MathKernel","-noprompt","-initfile","rankCombo.nb"])
    #with open("rankCombo.txt", 'r') as f:
    #    ranks = [int(line.strip()) for line in f]

    #print 'RESULTS'
    #print ranks
    return ranks

