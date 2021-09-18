# Isomorphism based generated network verifier for two-layer network

###################################
######      DEPENDENCIES     ######
###################################

# for running executable, with parameters
import subprocess
# for representation and graph operations
import networkx as nx
# for switch count calculation in butterfly topology
from math import log2
# for easy errors
from os   import error

##############################
######     CONSTANTS    ######
##############################

# number of tests
TESTCOUNT = 1
# directory for tests
TESTDIR   = 'tests'
# executable which shall generate Network file
EXEC      = './generator.py'

# file for inner topologies
SPECLOW  = 'L0Topology.txt'
# file for outer topology
SPECHIGH = 'L1Topology.txt'
# file for expected network
SPECEXP  = 'ExpectedNetwork.txt'
# file for generated network
SPECOUT  = 'Network.txt'

# chars indicating topology types, just for convenience
T_C = 'C'
T_R = 'R'
T_M = 'M'
T_F = 'F'
T_H = 'H'
T_B = 'B'

# number of chars to ignore when parsing the lines
# "Links: <integer>"
# "NodeID: <identifier>"
IGN_LINKS  = 7
IGN_NODEID = 8

##############################
######      HELPERS     ######
##############################

# reads a file and returns its contents as string
def fileStr(f):
    # open the given file, read only
    f = open(f, 'r')
    # read into a string
    s = f.read()
    # free the lock on the file
    f.close()

    return s
## END DEF


# parses a single line in a topology-describing file
def parseTopologyLine(s):
    # split according to SPACEs
    s = s.split(' ')
    # return X:str, n:int, m:int
    return (s[0], int(s[1]), int(s[2]))
## END DEF


# from a tuple (X, n, m) describing a topology,
# returns the number of nodes expected in the network
def nodeCount(t):
    # if not a butterfly or a hypercube,
    # total nodes are the product of the nodes in each dimension
    if (t[0] != T_B) or (t[0] != T_H):
        return t[1] * t[2]

    # if hypercube, has 8 nodes only
    if (t[0] == T_H):
        return 8
    
    # if butterfly, has 1 in/out layer and log2(n) switch layers
    # each layer has n nodes
    return (1 + log2(t[1])) * t[1]
## END DEF


# given a string with the contents of the generated network file
# parses it into a graph, with sanity checks along the way
def parseNetwork(s, total):
    # initialize graph
    G = nx.DiGraph()

    # currnode  : the current node from whom we're adding edges to others
    # edgecount : the number of edges remaining to be added from current node
    # encnodes  : the total number of nodes encountered in the input
    currnode  = 'error'
    edgecount = 0
    encnodes  = 0

    # parse each line
    for i in s.split('\n'):
        # Line style: NodeID: <identifier>
        # Action:     Add a node
        if i[0] == 'N':
            # sanity check before starting with a new node
            if edgecount > 0:
                error(f'not enough edges for node: {currnode}, remaining: {edgecount}')

            # add node to graph
            G.add_node(i[IGN_NODEID:])
            # set currnode
            currnode = i[IGN_NODEID:]
            # increment encountered nodes count
            encnodes += 1

        # Line style: Links: <integer>
        # Action:     Set edge count
        elif i[1] == 'i':
            # count of edges
            edgecount = int(i[IGN_LINKS:])

        # Line style: L(<integer>): <identifier>
        # Action:     Add a directed edge
        elif i[1] == '(':
            # add a link
            G.add_edge(currnode, i.split(':')[1][1:])
            # one less link remaining
            edgecount -= 1

        # Line style: *
        # Action:     ERROR
        else:
            # ERROR
            error('umm weird input: ' + i)
        
        # sanity check: don't add more edges than reported
        if edgecount < 0:
            error('too many edges for node: ' + currnode)
    ## END FOR

    # if total encountered nodes were not as many as expected
    if encnodes != total:
        # ERROR
        error(f'expected {total} nodes, got {encnodes}')

    # graph fully constructed
    return G
## END DEF


##############################
######      TESTING     ######
##############################

for i in range(TESTCOUNT):
    # prompt test count
    print(f'T#{i}: ', end='')

    # testdir: stores relative path to current test folder
    testdir = TESTDIR + '/' + str(i) + '/'
    # run the executable, with topology input files from testdir
    subprocess.run([EXEC, testdir + SPECLOW, testdir + SPECHIGH])

    # read outer network topology parameters from given file in testdir
    specOut = parseTopologyLine(fileStr(testdir + SPECHIGH))
    # stores total expected nodes in graph (includes switches)
    totalNodes = 0

    # only in the case of butterfly, the total node count
    # will not be the sum of all the inner topology node counts
    if specOut[0] == T_B:
        # in that case, we have some extra switches
        # for the outer topology.
        # add them
        totalNodes = nodeCount(specOut) - specOut[1]

    # now for the inner topologies
    specIn  = []
    # for each line in the input file
    for i in fileStr(testdir + SPECLOW).split('\n'):
        # parse the line for parameters and add them to specIn
        specIn.append(parseTopologyLine(i))
        # also increment total node count
        totalNodes += nodeCount(specIn[len(specIn) - 1])

    # parse the Network files generated by the executable
    # and from the test case (Expected Network)

    # we use networkx library to save time reimplementing directed graphs
    # totalNodes are passed just as a sanity check
    network1 = parseNetwork(fileStr(SPECOUT), totalNodes)
    network2 = parseNetwork(fileStr(testdir + SPECEXP), totalNodes)

    # check with the fastest method for isomorphism
    if nx.faster_could_be_isomorphic(network1, network2) == False:
        print('FAIL: faster, isomorphism')
        continue
    else:
        # 1st test passed this one
        print('P1 ', end='')
    
    # if the previous passed, check with a slightly more thorough approach
    if nx.fast_could_be_isomorphic(network1, network2) == False:
        print('FAIL: fast, isomorphism')
        continue
    else:
        # 2nd test ok
        print('P2 ', end='')

    # if that passed also, check with another slower approximate check
    if nx.could_be_isomorphic(network1, network2) == False:
        print('FAIL: regular, isomorphism')
        continue
    else:
        # 3rd test ok
        print('P3 ', end='')

    # and if all the previous ones passed, thoroughly check for isomorphism
    if nx.is_isomorphic(network1, network2) == False:
        print('FAIL: full test, isomorphism')
        continue
    else:
        # all good
        print('ALL OK')
## END FOR