__author__ = 'Natalie'
import graphModel
import candidate
import networkx
import itertools


def kbits(n, k):
    result = []
    for bits in itertools.combinations(range(n), k):
        s = [0] * n
        for bit in bits:
            s[bit] = 1
        result.append(s)
    return result

def chunker(iterable, chunksize, filler):
    return itertools.izip_longest(*[iter(iterable)]*chunksize, fillvalue=filler)

def kmats(m, n, k):
    return [[list(k) for k in chunker(q, n, 0)] for q in kbits(m*n,k)]


def generateAllGraphs(origGraph, dimension, minParam, maxParam):
    #first generate all of the matrices
    allMat = []
    maxParam = maxParam + 1
    for i in range(minParam, maxParam):
        allMat.append(kmats(dimension, dimension, i))

    #then iterate through them creating a candidate
    allCandidates = []
    for mat in allMat:
        for singMat in mat:
            #dont add the same matrix that we want to be compared against
            if not (networkx.to_numpy_matrix(origGraph) == singMat).all():
                allCandidates.append(candidate.candidate(singMat))

    return allCandidates


# PROBLEM
def findNumPathsToObs(model, obs):
    #obs is the C matrix, to translate this to nodes we want to
    #find all of the columns that have a 1, the number column is the number node
    obsnodes = []
    colCount = 0

    #print 'all edges'
    #print list(model.myGraph.edges())


    for i in obs.T:
        if i.any() == 1 and not colCount in obsnodes:
            obsnodes.append(colCount)
        colCount = colCount + 1

    #print 'observed nodes are'
    #print obsnodes

    totPaths = 0
    allNumPaths = []
    for currObsNode in obsnodes:
        numPaths = 0
        for currNode in model.myGraph.nodes():
            #(G, source, target)
            if currNode != currObsNode and networkx.has_path(model.myGraph, currNode, currObsNode):
                #print 'path from %d to %d' % (currNode, currObsNode)
                totPaths = totPaths + 1
                numPaths = numPaths + 1
            #else:
                #print 'NO path from %d to %d' % (currNode, currObsNode)
        allNumPaths.append(numPaths)

    #print 'all the paths'
    #print allNumPaths
    return allNumPaths
    #return totPaths

def findNumPathsFromIn(model, input):
    #input is the B matrix, to translate this to nodes we want to
    #find all of the columns that have a 1, the number column is the number node
    obsnodes = []
    colCount = 0


    for i in input.T:
        if i.any() == 1 and not colCount in obsnodes:
            obsnodes.append(colCount)
        colCount = colCount + 1


    allNumPaths = []
    for currObsNode in obsnodes:
        numPaths = 0
        for currNode in model.myGraph.nodes():
            if currNode != currObsNode and networkx.has_path(model.myGraph, currObsNode, currNode):
                numPaths = numPaths + 1
        allNumPaths.append(numPaths)
    return allNumPaths


def ensureInputConn(model, input):
    #input is the B  matrix, to translate this to nodes we want to
    #find all of the columns that have a 1, the number column is the number node
    inputnodes = []
    colCount = 0


    for i in input.T:
        if i.any() == 1 and not colCount in inputnodes:
            inputnodes.append(colCount)
        colCount = colCount + 1

    hasPath = True
    for currNode in model.myGraph.nodes():
        for currInNode in inputnodes:
            if currNode != currInNode and not networkx.has_path(model.myGraph, currInNode, currNode):
                hasPath = False
                break

    return hasPath

def ensureOutputConn(model, input):
    #input is the C  matrix, to translate this to nodes we want to
    #find all of the columns that have a 1, the number column is the number node
    inputnodes = []
    colCount = 0

    for i in input.T:
        if i.any() == 1 and not colCount in inputnodes:
            inputnodes.append(colCount)
        colCount = colCount + 1

    hasPath = True
    for currNode in model.myGraph.nodes():
        for currInNode in inputnodes:
            if currNode != currInNode and not networkx.has_path(model.myGraph, currNode, currInNode):
                hasPath = False
                break

    return hasPath


def shortestInOutPaths(model, input, output):
    shortestPaths = []
    inputnodes = []
    outputnodes = []
    colCount = 0

    for i in input.T:
        if i.any() == 1 and not colCount in inputnodes:
            inputnodes.append(colCount)
        colCount = colCount + 1

    colCount = 0
    for i in output.T:
        if i.any() == 1 and not colCount in outputnodes:
            outputnodes.append(colCount)
        colCount = colCount + 1


    for i in inputnodes:
        for o in outputnodes:
            if i != o:
                #from perturbed to the inputs
                shortestPaths.append(networkx.all_shortest_paths(model.myGraph, i, o))

    return shortestPaths

def findNumTraps(model):
    graph = model.myGraph
    numTraps = 0
    #first see for single node trap
    for node in graph.nodes():
        numIn = len(graph.in_edges([node]))
        numOut = len(graph.out_edges([node]))

        if (node, node) in graph.in_edges([node]):
            numIn = numIn - 1

        if numIn > 0 and numOut == 0:
            numTraps = numTraps + 1


    strgComps = networkx.strongly_connected_components(graph)
    for comp in strgComps:
        if len(comp) < len(graph.nodes())and len(comp) > 1:
            numIn = len(graph.in_edges(comp))
            numOut = len(graph.out_edges(comp))
            for node1 in comp:
                for node2 in comp:
                    if (node1, node2) in graph.in_edges([node2]):
                        numIn = numIn - 1
                    if (node2, node1) in graph.in_edges([node2]):
                        numIn = numIn - 1

                    if (node1, node2) in graph.out_edges([node2]) and node1 != node2:
                        numOut = numOut - 1
                    if (node2, node1) in graph.out_edges([node2]) and node1 != node2:
                        numOut = numOut - 1

            if numIn > 0 and numOut == 0:
                numTraps = numTraps + 1

    return numTraps



