from StringIO import StringIO
import re
from compgraph_web.settings import DISTRIBUTED

__author__ = 'Natalie'

import scipy
import numpy
import sympy
import graphModel
import graphTools
import networkx
import laplaceTools

# bring in the distributed task processor
from computation.tasks import processSingleTotalJacobian

def default_notify(msg):
    print msg

def processInput(data, notify=default_notify):
    # take in the data in the given format and extract all of the fields from it
    inputParams = [re.sub(r"\s\s+", " ", str(line.strip().split('=')[1])) for line in data.split('\n')]

    A = scipy.mat(inputParams[0])
    B = scipy.mat(inputParams[1])
    C = scipy.mat(inputParams[2])
    tempAdj = scipy.mat(inputParams[3])
    AdjMat = tempAdj.T

    n = B.size
    m = scipy.count_nonzero(B)
    newB = scipy.zeros((n,m))
    cnt = 0
    rng = scipy.arange(n)
    for i in rng:
      if B[i,0]==1:
        newB[i,cnt] = 1
        cnt=cnt+1
    B = scipy.mat(newB)
    B=B.astype(int)

    n = C.size
    m = scipy.count_nonzero(C)
    newC = scipy.zeros((m,n))
    cnt = 0
    rng = scipy.arange(n)
    for i in rng:
      if C[0,i]==1:
        newC[cnt,i] = 1
        cnt=cnt+1
    C = scipy.mat(newC)
    C=C.astype(int)

    #num compartments
    n = int(inputParams[4])

    #num inputs
    r = int(inputParams[5])

    #num outputs
    m = int(inputParams[6])

    output = StringIO()

    #A = scipy.mat('[1 1 0 0; 1 1 0 0; 1 0 1 1; 0 0 1 1]')
    #B = scipy.mat('[1; 0; 0; 0]')
    #C = scipy.mat('[1 0 0 0; 0 0 1 0]')

    #in adjMat we need to replace all Aii's with the leaks
    #AdjMat = A.T


    #num compartments
    #n = 4

    #num inputs
    #r = 1

    #num outputs
    #m = 2

    notify(" => Inside input processor!")

    # ============================================================================
    # === STEP 1. generate the original graph model
    # ============================================================================

    #after this everything we need is computed, the Jacobian, alphas, betas, etc
    myGraphModel = graphModel.graphModel(A, B, C, n, r, m, AdjMat, notify=notify)

    notify(" => completed graphModel.graphModel")
#     ######
# 	##MB Additions/Modifications
# #    if myGraphModel.QRank != n:
# #        output.write('q rank != n nonobservable')
# #        notify('q rank != n nonobservable')
# #        notify('process ended')
# #        return "model nonobservable"
# #
# #    if myGraphModel.RRank != n:
# #        output.write('r rank != n noncontrollable')
# #        notify('r rank != n noncontrollable')
# #        notify('process ended')
# #        return "model noncontrollable"
#
#
#     if laplaceTools.hasComplexEigenvalues(A):
#         output.write('Complex eigenvalues--not all models may be discovered! (Michael Bilow)')
#     ## <end> MB Additions/Modifications

    nonobservable = False
    noncontrollable = False

    if myGraphModel.QRank != n:
        output.write('q rank != n nonobservable')
        notify('q rank != n nonobservable')
        nonobservable = True

    if myGraphModel.RRank != n:
        output.write('r rank != n noncontrollable')
        notify('r rank != n noncontrollable')
        noncontrollable = True

    if noncontrollable or nonobservable:
        notify('process ended')

        error_msg = "%s %s" % (
            "model nonbservable" if nonobservable else "",
            "model noncontrollable" if noncontrollable else ""
        )
        return error_msg

    notify('DONE MAKING ORIG MODEL')

    notify(n)
    notify(myGraphModel.Rank)

    # ============================================================================
    # === STEP 2. generate all other graphs, check properties
    # ============================================================================

    allCandidates = graphTools.generateAllGraphs(myGraphModel.myGraph, n, myGraphModel.Rank, myGraphModel.Rank)
    notify('my original model graph (transposed)')
    notify( networkx.to_numpy_matrix(myGraphModel.myGraph))
    notify('my original model edges')
    notify(list(myGraphModel.myGraph.edges()))
    #find number of paths from node to observation
    numOrigPathsToObs = graphTools.findNumPathsToObs(myGraphModel, C)

    #make sure every node has a path from an input, to itself
    hasInputConnOrig = graphTools.ensureInputConn(myGraphModel, B)

    #find number of paths from the input node to the other nodes
    numOrigPathsFromInput = graphTools.findNumPathsFromIn(myGraphModel, B)

    #make sure every node has a path from an output, to itself
    hasOuputConnOrig = graphTools.ensureOutputConn(myGraphModel, C)

    #compare the shortest paths
    shortestPathsOrig = graphTools.shortestInOutPaths(myGraphModel, B, C)
    origPathsList = []

    if len(shortestPathsOrig) > 0:
        try:
            origPathsList.append([p for p in shortestPathsOrig[0]])
        except networkx.exception.NetworkXNoPath:
            notify("No Orig Path")
    else:
        output.write('No path from input to output in the original graph')
        output.close()
        exit


    #find number of traps
    numTrapsOrig = graphTools.findNumTraps(myGraphModel)
    passGraphCand = []

    numPathToObsWrong = 0
    numhasInputConnWrong = 0
    numCandPathsFromInputWrong = 0
    hasOuputConnWrong = 0
    numTrapsWrong = 0
    numPathsListWrong = 0

    notify('number of candidates: %d' % len(allCandidates))
    output.write('num of candidates %d' % len(allCandidates))
    output.write('\n')

    # if we never had any candidates, terminate here
    if len(allCandidates) <= 0:
        result = output.getvalue()
        output.close()
        return result

    for candidate in allCandidates:
        #find number of paths from node to observation
        numCandPathsToObs = graphTools.findNumPathsToObs(candidate, C)

        #make sure every node has a path from an input, to itself
        hasInputConn = graphTools.ensureInputConn(candidate, B)

        #find number of paths from the input node to the other nodes
        numCandPathsFromInput = graphTools.findNumPathsFromIn(candidate, B)

        #make sure every node has a path from an output, to itself
        hasOuputConn = graphTools.ensureOutputConn(candidate, C)

        #compare the shortest paths
        shortestPaths = graphTools.shortestInOutPaths(candidate, B, C)

        #find number of traps took 3620 out
        numTraps = graphTools.findNumTraps(candidate)

        origListResult = (numOrigPathsToObs, hasInputConnOrig, numOrigPathsFromInput, hasOuputConnOrig, numTrapsOrig)
        candListResult = (numCandPathsToObs, hasInputConn, numCandPathsFromInput, hasOuputConn, numTraps)

        candPathsList = []

        try:
            candPathsList.append([q for q in shortestPaths[0]])
        except networkx.exception.NetworkXNoPath:
            a = 1


        if numOrigPathsToObs != numCandPathsToObs:
            numPathToObsWrong = numPathToObsWrong + 1
        if hasInputConnOrig != hasInputConn:
            numhasInputConnWrong = numhasInputConnWrong + 1
        if numOrigPathsFromInput != numCandPathsFromInput:
            numCandPathsFromInputWrong = numCandPathsFromInputWrong + 1
        if hasOuputConnOrig != hasOuputConn:
            hasOuputConnWrong = hasOuputConnWrong + 1
        if origPathsList != candPathsList:
            numPathsListWrong = numPathsListWrong + 1
        if numTrapsOrig != numTraps:
            numTrapsWrong = numTrapsWrong + 1


        #paths match
        if origPathsList == candPathsList:
            #all other results equal
            #if numOrigPathsToObs == numCandPathsToObs and hasInputConnOrig == hasInputConn and numOrigPathsFromInput == numCandPathsFromInput:
            #    if hasOuputConnOrig == hasOuputConnOrig and numTrapsOrig == numTraps:
            #        passGraphCand.append(candidate)
            #if numOrigPathsToObs == numCandPathsToObs:
            #    passGraphCand.append(candidate)
            if origListResult == candListResult:
                passGraphCand.append(candidate)



    notify('num of candidates left after graph properties checked: %d out of %d' % (len(passGraphCand), len(allCandidates)))
    output.write('num of candidates left after graph properties checked: %d out of %d' % (len(passGraphCand), len(allCandidates)))
    output.write('\n')

    output.write('number of candidates that had incorrect # paths to obs %d' % numPathToObsWrong)
    output.write('\n')

    output.write('number of candidates that dont have input connectivity %d' % numhasInputConnWrong)
    output.write('\n')

    output.write('number of candidates that had incorrect # paths from input %d' % numCandPathsFromInputWrong)
    output.write('\n')

    output.write('number of candidates that dont have output connectivity %d' % hasOuputConnWrong)
    output.write('\n')

    output.write('number of candidates that have incorrect # traps %d' % numTrapsWrong)
    output.write('\n')

    output.write('number of candidates that have incorrect shortestpaths %d' % numPathsListWrong)
    output.write('\n')

    # if we don't have any candidates left, terminate here
    if len(passGraphCand) <= 0:
        result = output.getvalue()
        output.close()
        return result

    # ============================================================================
    # === STEP 3. check alphas, betas
    # ============================================================================

    numRank = 0
    rankFailedCand = None
    passLaplaceCand = []
    failAlphaLaplaceCand = []
    failBetaLaplaceCand = []

    for cand in passGraphCand:
        #step one rank(A|B) = n
        candAB = laplaceTools.makeSymMat(numpy.append(cand.A, B, axis=1))

        #if (cand.A == myMatch).all() or (cand.A == myMatch2).all() or (cand.A == myMatch4).all():
        #    print "--------------FOUND MATCH!!!!!--------------"
        #    candTF, candCharEqn, candAlphas, candBetas = laplaceTools.calcTF(cand.A, B, C, n)
        #    print candAlphas
        #    print candBetas
        #    print candTF
        #    print cand.A

        # candABRank = laplaceTools.calcRank(candAB)
        candABRank = n
        if candABRank == n:
            #step 2 compare the moment invariants!
            candTF, candCharEqn, candAlphas, candBetas = laplaceTools.calcTF(cand.A, B, C, n)
            cand.Alphas = candAlphas
            cand.Betas = candBetas

            #print "Alpha Keys"
            currNum = 0
            alphasMatch = True
            candAlphaKeysList = []
            for currDict in candAlphas:
                candAlphaKeys = laplaceTools.getOrderedKeys(currDict)
                #print candAlphaKeys
                #print myGraphModel.alphaKeys[currNum]
                candAlphaKeysList.append(candAlphaKeys)
                if candAlphaKeys != myGraphModel.alphaKeys[currNum]:
                    alphasMatch = False

                currNum = currNum + 1


            #print "Beta Keys"
            currNum = 0
            for currDict in candBetas:
                #print laplaceTools.getOrderedKeys(currDict)
                #print myGraphModel.betaKeys[currNum]
                currNum = currNum + 1

            if alphasMatch:
                currNum = 0
                candBetaKeysList = []
                betasMatch = True
                for currDict in candBetas:
                    candBetaKeys = laplaceTools.getOrderedKeys(currDict)
                    candBetaKeysList.append(candBetaKeys)
                    if candBetaKeys != myGraphModel.betaKeys[currNum]:
                        betasMatch = False

                    currNum = currNum + 1

                if betasMatch:
                    passLaplaceCand.append(cand)
                    #print len(passLaplaceCand)
                    #print 'FOUND CANDIDATE'
                    #print candTF
                    #print cand.A
                    #print candAlphaKeysList
                    #print candBetaKeysList

    notify('the alphas: %s' % str(myGraphModel.alphaKeys))
    notify('the betas: %s' % str(myGraphModel.betaKeys))
    output.write('the alphas: %s' % str(myGraphModel.alphaKeys))
    output.write('\n')
    output.write('the betas: %s' % str(myGraphModel.betaKeys))
    output.write('\n')

    notify('num of candidates left alpha betas checked: %d out of %d' % (len(passLaplaceCand), len(allCandidates)))
    output.write('num of candidates left alpha betas checked %d out of %d' % (len(passLaplaceCand), len(allCandidates)))
    output.write('\n')

    # if we don't have any candidates left, terminate here
    if len(passLaplaceCand) <= 0:
        result = output.getvalue()
        output.close()
        return result

    # ============================================================================
    # === STEP 3. check submatrix jacobians
    # ============================================================================

    passJacobianRank = []
    for cand in passLaplaceCand:
        #now calculate the jacobian
        cand.calcJacobianRank()
        if myGraphModel.Rank == cand.Rank:
            passJacobianRank.append(cand)

    notify('num of candidates left after calc rank full jacobian: %d out of %d' % (len(passJacobianRank), len(allCandidates)))
    output.write('num of candidates left after calc rank full jacobian %d out of %d' % (len(passJacobianRank), len(allCandidates)))
    output.write('\n')

    # if we don't have any candidates left, terminate here
    if len(passJacobianRank) <= 0:
        result = output.getvalue()
        output.close()
        return result

    notify("About to compute laplaceTools.reducedJacMat()...")

    #first get the simplified jacobian
    myGraphModel.Jac = laplaceTools.reducedJacMat(myGraphModel.Jac)

    notify("About to compute laplaceTools.calcAllSubranks()...")

    #get the ranks
    myGraphModel.JacComboRanks = laplaceTools.calcAllSubranks(myGraphModel.Jac, myGraphModel.Rank)

    notify("About to process candidates (distributed: %s)..." % DISTRIBUTED)

    if DISTRIBUTED:
        # compute ranks of all submatrices of the jacobian of the original model
        passSubJacobianRankTask = processSingleTotalJacobian.chunks([(myGraphModel, i) for i in passJacobianRank], 10)()
        result = passSubJacobianRankTask.get()
        passSubJacobianRank = [item for sublist in result for item in sublist if item]
    else:
        # for now, we'll do it in the non-iterative way
        passSubJacobianRank = [x for x in [processSingleTotalJacobian(myGraphModel, i) for i in passJacobianRank] if x is not None]

    notify('num of candidates left at the end: %d out of %d' % (len(passSubJacobianRank), len(allCandidates)))
    output.write('num of candidates left at the end: %d out of %d' % (len(passSubJacobianRank), len(allCandidates)))
    output.write('\n')

    # if we don't have any candidates left, terminate here
    if len(passSubJacobianRank) <= 0:
        result = output.getvalue()
        output.close()
        return result

    output.write('Adjacency graphs\n')
    output.write('Original Model\n')
    output.write("%s\n" % str(networkx.to_numpy_matrix(myGraphModel.myGraph).T))
    output.write('A matrix %s \n' % str(myGraphModel.A))
    output.write('\n')

    for i, cand in enumerate(passSubJacobianRank):
        output.write('Model %d \n' % (i+1))
        output.write(str(networkx.to_numpy_matrix(cand.myGraph).T))
        output.write('\n')
        output.write('A matrix \n%s \n' % str(cand.A))
        output.write('\n')
        output.write('\n')

    result = output.getvalue()
    output.close()

    return result
