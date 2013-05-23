from StringIO import StringIO

__author__ = 'Natalie'

import scipy
import numpy
import sympy
import graphModel
import graphTools
import networkx
import laplaceTools

def processInput(data):
    # take in the data in the given format and extract all of the fields from it
    inputParams = [str(line.strip().split('=')[1]) for line in data.split('\n')]

    A = scipy.mat(inputParams[0])
    B = scipy.mat(inputParams[1])
    C = scipy.mat(inputParams[2])
    tempAdj = scipy.mat(inputParams[3])
    AdjMat = tempAdj.T

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

    #after this everything we need is computed, the Jacobian, alphas, betas, etc
    myGraphModel = graphModel.graphModel(A, B, C, n, r, m, AdjMat)

    if myGraphModel.QRank != n:
        output.write('q rank != n nonobservable')
        print 'q rank != n nonobservable'
        print 'process ended'
        exit()
    if myGraphModel.RRank != n:
        output.write('r rank != n noncontrollable')
        print 'r rank != n noncontrollable'
        print 'process ended'
        exit()
    print 'DONE MAKING ORIG MODEL'


    print n
    print myGraphModel.Rank

    allCandidates = graphTools.generateAllGraphs(myGraphModel.myGraph, n, myGraphModel.Rank, myGraphModel.Rank)
    print 'my original model graph (transposed)'
    print  networkx.to_numpy_matrix(myGraphModel.myGraph)
    print 'my original model edges'
    print list(myGraphModel.myGraph.edges())
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
            print "No Orig Path"
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

    print ('number of candidates', len(allCandidates))
    output.write('num of candidates %d' % len(allCandidates))
    output.write('\n')
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



    print ('num of candidates left after graph properties checked', len(passGraphCand), 'out of', len(allCandidates))
    output.write('num of candidates left after graph properties checked %d output %d' % (len(passGraphCand), len(allCandidates)))
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



    print ('num of candidates left alpha betas checked', len(passLaplaceCand), 'out of', len(allCandidates))
    output.write('num of candidates left alpha betas checked %d output %d' % (len(passLaplaceCand), len(allCandidates)))
    output.write('\n')
    passJacobianRank = []
    for cand in passLaplaceCand:
        #now calculate the jacobian
        cand.calcJacobianRank()
        if myGraphModel.Rank == cand.Rank:
            passJacobianRank.append(cand)

    print ('num of candidates left after calc rank full jacobian', len(passJacobianRank), 'out of', len(allCandidates))
    output.write('num of candidates left after calc rank full jacobian %d output %d' % (len(passJacobianRank), len(allCandidates)))
    output.write('\n')
    #first get the simplified jacobian
    myGraphModel.Jac = laplaceTools.reducedJacMat(myGraphModel.Jac)
    #get all the combos
    allCombos = laplaceTools.kbits(myGraphModel.Jac.rows, myGraphModel.Rank)
    #get the ranks
    myGraphModel.JacComboRanks = laplaceTools.compareOverallRank(myGraphModel.Jac, myGraphModel.Rank, allCombos)
    passSubJacobianRank = []

    #print 'ORIG Jac Combo Ranks'
    #print len(myGraphModel.JacComboRanks)
    #print myGraphModel.JacComboRanks

    numPassed = 0
    tot = 0
    for cand in passJacobianRank:
        #first get the simplified jacobian
        cand.Jac = laplaceTools.reducedJacMat(cand.Jac)
        #get all the combos
        allCombos = laplaceTools.kbits(cand.Jac.rows, cand.Rank)
        #get the ranks
        cand.JacComboRanks = laplaceTools.compareOverallRank(cand.Jac, cand.Rank, allCombos)
        #print len(cand.JacComboRanks)
        #print 'cand cobo ranks'
        #print cand.JacComboRanks
        tot += 1
        if myGraphModel.JacComboRanks == cand.JacComboRanks:
            numPassed += 1
            print 'PASSED: %d / %d' % (numPassed, tot)
            passSubJacobianRank.append(cand)

    print ('num of candidates left at the end', len(passSubJacobianRank), 'out of', len(allCandidates))
    output.write('num of candidates left at the end %d output %d' % (len(passSubJacobianRank), len(allCandidates)))
    output.write('\n')
    output.write('Adjacency graphs\n')
    output.write('Original Model\n')
    output.write(str(networkx.to_numpy_matrix(myGraphModel.myGraph).T))
    output.write('\n')

    for i, cand in enumerate(passSubJacobianRank):
        output.write('Model %d \n' % i)
        output.write(str(networkx.to_numpy_matrix(cand.myGraph).T))
        output.write('\n')

    output.close()

    return str(output)
