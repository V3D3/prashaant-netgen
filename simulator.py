# monolithic simulator
#!/usr/bin/python
#####################################################################################################
#####################################################################################################
### Network on Chip - Project - 2
### Simulating transfer of a flit in a two level network of nodes
### Authors : Vedaant Alok Arya (CS19B046), Pole Praneeth, Shashank Nag (EE19B118)
###
###------------------------------------INPUT----------------------------
###The two input files:
### L1Topology.txt will have single line with this data
### X,n,m where X = C, R, M, F, H, B
### C: Chain, R: Ring, M: Mesh, F: Folded Torus, H: Hypercube of dimension 3 (8 nodes), B: Butterfly network
### n: Number of nodes in first dimension
### m: Number of nodes in second dimension - it is 1 for C and R.
### n = m = 3 for H and 
### n = m = 2^k  (Power of 2) for B for some k > 1
### L2Topology.txt will have n X m lines with each line as the same syntax as above.
###-
###-------------OUTPUT---------------------------------------
### All nodes in a single file. Each node described in the form
###******************
###NodeID: 
###Links: <Number of links> (say P of them)
###P lines of this format <L(i): Destination Node> 1<= i <= P
###**************************

### DEPENDENCIES: networkx, pydot

###Network types: RCMBFH (Ring Chain Mesh Butterfly FoldedTorus Hypercube)


#### IMPORTS


from math import log2
import networkx as nx

# for actual network, convention for
# node name: if connects to outside network
#               1<outID><DELIMITER><inID>
#               binary encoding: 1 <outID bits> <inID bits>
#               example: outside max nodes = 16, inside max nodes = 16
#               1 oooo ccc iiii
#               1 0101     0011
#            else
#               0<outID><DELIMITER><inID>
#               binary encoding: 0 <outID bits> <inID bits>
#               example: continued
#               0 0000     0010



#### CLASSES



class Node:
    def __init__(self, isHead, headID, inClass, inID, isSwitch = False):
        # is this node the head node of its tile?
        self.isHead = isHead
        # id of head node of the tile of this node in outer topology
        self.headID = headID
        # class of inner topology of which this node is a member
        self.inClass = inClass
        # id of node in inner topology
        self.inID = inID
        # is this node a switch or a tile?
        self.isSwitch = isSwitch

        # string id for this node, uniquely identifies it
        self.id = self.generateID(isHead, headID, inClass, inID, isSwitch)
      
    @staticmethod
    def generateID(isHead, headID, inClass, inID, isSwitch = False):
      if(isHead):
        return 'O' + headID + DELIMITER + inID
      else:
        return 'I' + headID + DELIMITER + inID

class Topology:
  def __init__(self, isOuter, headID, topoClass, topoParams, topoGraph):
    # is it an outer topology or inner?
    self.isOuter = isOuter
    # id of the head node in this tile (if exists)
    self.headID = headID
    # class of this topography
    self.topoClass = topoClass
    # parameters for this topology
    self.topoParams = topoParams
    # store the graph of the topology
    self.topoGraph = topoGraph



#### GLOBALS



# This object stores the outer topology
outerTopology = {}
# This dictionary stores inner topology objects
innerTopologies = {}
# The delimiter in string IDs
DELIMITER = 'Z'
# The input files
file1 = open(r"L1Topology.txt","r")  
file2 = open(r"L2Topology.txt","r")
L1 = file1.read()        # Read the L1 topology file to find the top layer topology

# The list final_nodes stores all the connections to a particular nodes (a list of list)
# The NodeID for each node is N<i>, where <i> is its position in the final_nodes list



#### TOPOLOGY GENERATOR FUNCTIONS



# Function to generate the tile for a chain type L2 connection
# f_nodes in the pointer to the first node in the particular tile in the final_nodes list
# n is the length of the chain
def chain_gen(n, id):
    thisClass = 'C'
    thisParams = (n, )
    thisGraph = nx.Graph();
    thisTopology = Topology(False, '', thisClass, thisParams, thisGraph);

    # List which stores a list of nodes connected to each node in the tile
    # Trivial case of one node. It isn't connected to anything
    if n == 1:
        node = Node(True, id, thisClass, '')
        thisGraph.add_node(node.id, exdata=node)
        thisTopology.headID = node.id
    else :
        #Add nodes
        for i in range(0, n):
          isHead = False
          if(i == int(n/2)):
            isHead = True
            thisTopology.headID = Node.generateID(True, id, thisClass, str(i))
          cnode = Node(isHead, id, thisClass, str(i))
          thisGraph.add_node(cnode.id, exdata=cnode)

        #Add edges between nodes
        for i in range(0, n-1):
          myID = Node.generateID((i == int(n/2)), id, thisClass, str(i))
          nextID = Node.generateID(((i+1) == int(n/2)), id, thisClass, str(i+1))

          thisGraph.add_edge(myID, nextID)

    #Returning the tile and pointer to head_node
    innerTopologies[id] = thisTopology


# Function to generate the tile for a ring type L2 connection
# n is the length of the ring
def ring_gen(n, id):
    thisClass = 'R'
    thisParams = (n, )
    thisGraph = nx.Graph()
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph)
    
    #Trivial case of one node
    if n == 1:
      node = Node(True, id, thisClass, '')
      thisGraph.add_node(node.id, exdata=node)
      thisTopology.headID = node.id
    #Ring with only two nodes. The nodes are connected to each other
    if n == 2:
      #Generate and add the two nodes
      node1 = Node(False, id, thisClass, '0')
      node2 = Node(True, id, thisClass, '1')
      thisGraph.add_node(node1.id, exdata=node1)
      thisGraph.add_node(node2.id, exdata=node2)
      thisTopology.headID = node2.id
      #Link them
      thisGraph.add_edge(node1.id, node2.id)

    #Non trivial case
    else :
      #Adding nodes, P1: headnode
      headnode = Node(True, id, thisClass, '0')
      thisGraph.add_node(headnode.id, exdata=headnode)
      thisTopology.headID = headnode.id
      #Adding nodes, P2: others
      for i in range(1, n):
        cnode = Node(False, id, thisClass, str(i))
        thisGraph.add_node(cnode.id, exdata=cnode)

      #Adding links except to head
      for i in range(1, n-1):
        myID = Node.generateID(False, id, thisClass, str(i))
        nextID = Node.generateID(False, id, thisClass, str(i + 1))
        thisGraph.add_edge(myID, nextID)
      #Adding links to head
      thisGraph.add_edge(headnode.id, Node.generateID(False, id, thisClass, str(n-1)))
      thisGraph.add_edge(headnode.id, Node.generateID(False, id, thisClass, str(1)))

    innerTopologies[id] = thisTopology



# Function to generate the tile for a hypercube type L2 connection
# Dimension is forced as 3 (8 nodes)
# f_nodes is the pointer to the first node in the Hypercube
def hypercube_gen(id):
    thisClass = 'H'
    thisParams = None
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);
    
    #Create and add nodes
    nodes = [Node(True, id, thisClass, '0')]
    thisGraph.add_node(nodes[0].id, exdata=nodes[0])
    thisTopology.headID = nodes[0].id

    for i in range(1, 8):
      nodes.append(Node(False, id, thisClass, str(i)))
      thisGraph.add_node(nodes[i].id, exdata=nodes[i])

    for i in range(8):
      #Edges by inverting 1 bit in each position
      #3 edges for our 3d hypercube
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 1].id)
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 2].id)
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 4].id)

    innerTopologies[id] = thisTopology


# Function to generate the tile for a mesh type L2 connection
# Dimension of n x m (n rows and m columns)
# f_nodes is the pointer to the first node in the Hypercube
def mesh_gen(n, m, id):
    thisClass = 'M'
    thisParams = (n, m)
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

    def checkHead(ix, jx):
      return (ix == int(n/2)) and (jx == (int(m/2)))

    #Add nodes
    for i in range(n):
      for j in range(m):
        isHead = checkHead(i, j)
        if(isHead):
          thisTopology.headID = Node.generateID(True, id, thisClass, str(i) + DELIMITER + str(j))
        cnode = Node(isHead, id, thisClass, str(i) + DELIMITER + str(j))
        thisGraph.add_node(cnode.id, exdata=cnode)

    #Checks if node is valid
    def checkNode(ix, jx):
      if(ix < 0 or jx < 0):
        return False
      if(ix >= n or jx >= m):
        return False
      return True

    #Safely adds edges - if dest node exists, and accounting for headID
    def addEdgeSafe(isrc, jsrc, idest, jdest):
      if(not checkNode(idest, jdest)):
        return
      srcID = Node.generateID(checkHead(isrc, jsrc), id, thisClass, str(isrc) + DELIMITER + str(jsrc))
      destID = Node.generateID(checkHead(idest, jdest), id, thisClass, str(idest) + DELIMITER + str(jdest))
      thisGraph.add_edge(srcID, destID)

    #Add edges
    for i in range(n):
      for j in range(m):
        addEdgeSafe(i, j, i - 1, j)
        addEdgeSafe(i, j, i + 1, j)
        addEdgeSafe(i, j, i, j - 1)
        addEdgeSafe(i, j, i, j + 1)

    innerTopologies[id] = thisTopology


# Function to generate the tile for a butterfly type L2 connection
def butterfly_gen(n, id):
  thisClass = 'B'
  thisParams = (n, )
  thisGraph = nx.Graph();
  thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

  # node internal IDs: <num1> :
  #   num1 identifies the node index
  # switch internal IDs: <num1> Z <num2> :
  #   num1 identifies the stage in the butterfly
  #   num2 identifies the switch in the stage

  thisTopology.headID = Node.generateID(True, id, thisClass, str(0))
  def checkHead(stage, index):
    if(stage == 0 and index == 0):
      return True
    return False

  #n/2 nodes on left, n/2 on right, n/4 switches in each stage
  #hence, log2(n/4) + 1 = log2(n) - 1 layers of switches
  #and 2 layers of nodes, total log2(n) + 1 layers
  n_stages = int(log2(n)) + 1

  #Add nodes
  for i in range(0, n):
    cnode = Node(checkHead(0 if i < int(n/2) else n_stages - 1, i % int(n/2)),
                  id, thisClass, str(i))
    thisGraph.add_node(cnode.id, exdata=cnode)
  #Add switches
  for i in range(1, n_stages - 1):
    for j in range(int(n/4)):
      cswitch = Node(False, id, thisClass, str(i) + DELIMITER + str(j), True)
      thisGraph.add_node(cswitch.id, exdata=cswitch)
  
  #Add edges from input to first switch layer
  for i in range(0, int(n/2)):
    nodeID = Node.generateID(checkHead(0, i), id, thisClass, str(i))
    switchID = Node.generateID(False, id, thisClass, str(1) + DELIMITER + str(int(i/2)), True)
    thisGraph.add_edge(nodeID, switchID)
  
  #Add edges from last switch layer to output
  for i in range(0, int(n/4)):
    switchID = Node.generateID(False, id, thisClass, str(n_stages - 2) + DELIMITER + str(i), True)
    nodeID1 = Node.generateID(False, id, thisClass, str(int(n/2) + (2*i)))
    nodeID2 = Node.generateID(False, id, thisClass, str(int(n/2) + (2*i + 1)))
    
    thisGraph.add_edge(switchID, nodeID1)
    thisGraph.add_edge(switchID, nodeID2)

  def nextSwitch(current, stage):
    bit = 1 << (stage - 1)
    return bit ^ current

  #Add edges between switches in the inner layers
  for i in range(1, n_stages - 2):
    for j in range(0, int(n/4)):
      myID = Node.generateID(False, id, thisClass, str(i) + DELIMITER + str(j), True)
      nextIDDirect = Node.generateID(False, id, thisClass, str(i + 1) + DELIMITER + str(j), True)
      nextIDIndirect = Node.generateID(False, id, thisClass, str(i + 1) + DELIMITER + str(nextSwitch(j, i)), True)
      
      thisGraph.add_edge(myID, nextIDDirect)
      thisGraph.add_edge(myID, nextIDIndirect)

  innerTopologies[id] = thisTopology


# Function to generate the tile for a folded torus type L2 connection
# Dimension of n x m (n rows and m columns)
def folded_torus_gen(n, m, id):
    thisClass = 'F'
    thisParams = (n, m)
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

    # Node ID: <num1> <DELIM> <num2>
    #   num1 -> row of the node
    #   num2 -> column of the node

    def checkHead(i, j):
      if(i == 0 and j == 0):
        thisTopology.headID = Node.generateID(True, id, thisClass, '0Z0')
        return True
      return False

    #Add nodes
    for i in range(n):
      for j in range(m):
        cnode = Node(checkHead(i, j), id, thisClass, str(i) + DELIMITER + str(j))
        thisGraph.add_node(cnode.id, exdata=cnode)

    def safeAddEdge(isrc, jsrc, idest, jdest):
      idest = (idest + n) % n
      jdest = (jdest + m) % m

      srcID = Node.generateID(checkHead(isrc, jsrc), id, thisClass, str(isrc) + DELIMITER + str(jsrc))
      destID = Node.generateID(checkHead(idest, jdest), id, thisClass, str(idest) + DELIMITER + str(jdest))
      thisGraph.add_edge(srcID, destID)

    #Add edges in columns
    for j in range(m):
      #Add link to immediately next of first node
      safeAddEdge(0, j, 1, j)
      #Add links in internal nodes
      for i in range(int(n / 2) - 1):
        safeAddEdge(2*i, j, 2*i+2, j)
        safeAddEdge(2*i+1, j, 2*i+3, j)
      #Add link to prev of last node
      safeAddEdge(n-1, j, n-2, j)
    
    #Add edges in rows
    for i in range(n):
      #Add link to immediately next of first node
      safeAddEdge(i, 0, i, 1)
      #Add links in internal nodes
      for j in range(int(m / 2) - 1):
        safeAddEdge(i, 2*j, i, 2*j+2)
        safeAddEdge(i, 2*j+1, i, 2*j+3)
      #Add link to prev of last node
      safeAddEdge(i, m-1, i, m-2)

    innerTopologies[id] = thisTopology

def genInner(id):
  tileInfo = file2.readline()
  network_type, n, m = tileInfo.split(',')
  n = int(n)
  m = int(m)
  
  if network_type == 'R':
    ring_gen(n, id)
  elif network_type == 'C':
    chain_gen(n, id)
  elif network_type == 'M':
    mesh_gen(n, m, id)
  elif network_type == 'B':
    butterfly_gen(n, id)
  elif network_type == 'F':
    folded_torus_gen(n, m, id)
  elif network_type == 'H':
    hypercube_gen(id)

def getHeadNode(index):
  srcTopo = innerTopologies[index]
  srcHeadID = srcTopo.headID
  srcHeadNode = srcTopo.topoGraph.nodes[srcHeadID]
  return srcHeadNode['exdata']

## The following functions handle linkages for the L1 topology. The head nodes are already generated by the corresponding L2 topology functions, and the following functions just add additional head node <-> head node linkages

# For ring type L1 topology
def ring_head_gen(n):
  thisClass = 'R'
  thisParams = (n, )
  thisGraph = nx.Graph()
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph)

  if n == 2:
    #Generate the topologies
    genInner('0')
    node0 = getHeadNode('0')
    thisGraph.add_node('0', exdata=node0)
    genInner('1')
    node1 = getHeadNode('1')
    thisGraph.add_node('1', exdata=node1)

    #Add edge between them
    thisGraph.add_edge('0', '1')

  #Non trivial case
  else :
    #Adding nodes
    for i in range(n):
      genInner(str(i))
      node = getHeadNode(str(i))
      thisGraph.add_node(str(i), exdata=node)

    #Adding links
    for i in range(n):
      thisGraph.add_edge(str(i), str((i + 1) % n))

  return thisTopology


# For chain type L1 topology
def chain_head_gen(n):
  thisClass = 'C'
  thisParams = (n, )
  thisGraph = nx.Graph();
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph);

  if n >= 2:
    for i in range(n):
      genInner(str(i))
      node = getHeadNode(str(i))
      thisGraph.add_node(str(i), exdata=node)

    for i in range(0, n-1):
      thisGraph.add_edge(str(i), str(i+1))
  else:
    print("Bad dimensions for outer topology as chain")
    exit()
  return thisTopology


# For hypercube type L1 topology
def hypercube_head_gen():
  thisClass = 'H'
  thisParams = None
  thisGraph = nx.Graph();
  thisTopology = Topology(True, '', thisClass, thisParams, thisGraph);
  n = 8

  for i in range(n):
    genInner(str(i))
    node = getHeadNode(str(i))
    thisGraph.add_node(str(i), exdata=node)
  
  for i in range(n):
    thisGraph.add_edge(str(i), str(i ^ 1))
    thisGraph.add_edge(str(i), str(i ^ 2))
    thisGraph.add_edge(str(i), str(i ^ 4))

  return thisTopology

# For mesh type L1 topology
def mesh_head_gen(n,m):
  thisClass = 'M'
  thisParams = (n, m)
  thisGraph = nx.Graph();
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph);

  def genID(ix, jx):
    return str(ix) + DELIMITER + str(jx)

  for i in range(n):
    for j in range(m):
      genInner(genID(i, j))
      node = getHeadNode(genID(i, j))
      thisGraph.add_node(genID(i, j), exdata=node)

  def checkNode(ix, jx):
    if(ix < 0 or jx < 0):
      return False
    if(ix >= n or jx >= m):
      return False
    return True

  def addEdgeSafe(isrc, jsrc, idest, jdest):
    if(not checkNode(idest, jdest)):
      return
    thisGraph.add_edge(genID(isrc, jsrc), genID(idest, jdest))

  for i in range(n):
    for j in range(m):
      addEdgeSafe(i, j, i - 1, j)
      addEdgeSafe(i, j, i + 1, j)
      addEdgeSafe(i, j, i, j - 1)
      addEdgeSafe(i, j, i, j + 1)

  return thisTopology


# For Butterfly type L1 topology
def butterfly_head_gen(n):
  thisClass = 'B'
  thisParams = (n, )
  thisGraph = nx.Graph();
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph);

  n_stages = int(log2(n)) + 1

  for i in range(0,n):
    genInner(str(i))
    cnode = getHeadNode(str(i))
    thisGraph.add_node(str(i), exdata=cnode)

    # switch names: <num1> <DELIM> <num2> :
    #   num1 identifies the stage in the butterfly
    #   num2 identifies the switch in the stage

  def switchID(stage, index):
    return str(stage) + DELIMITER + str(index)

  for i in range(1, n_stages - 1):
    for j in range(0, int(n/4)):
      thisGraph.add_node(str(i), exdata=Node(True, switchID(i, j), thisClass, '', True))
  
  #Add edges from input to first switch layer
  for i in range(0, int(n/2)):
    myID = Node.generateID(True, switchID(1, int(i/2)), thisClass, '', True)
    thisGraph.add_edge(str(i), myID)
  
  #Add edges from last switch layer to output
  for i in range(0, int(n/4)):
    myID = Node.generateID(True, switchID(n_stages - 2, i), thisClass, '', True)
    nodeID1 = str(int(n/2) + 2*i)
    nodeID2 = str(int(n/2) + 2*i + 1)
    
    thisGraph.add_edge(myID, nodeID1)
    thisGraph.add_edge(myID, nodeID2)

  def nextSwitch(current, stage):
    bit = 1 << (stage - 1)
    return bit ^ current

  #Add edges between switches in the inner layers
  for i in range(1, n_stages - 2):
    for j in range(0, int(n/4)):
      myID = Node.generateID(True, switchID(i, j), thisClass, '', True)
      nextIDDirect = Node.generateID(True, switchID(i+1, j), thisClass, '', True)
      nextIDIndirect = Node.generateID(True, switchID(i+1, nextSwitch(j, i)), thisClass, '', True)
      
      thisGraph.add_edge(myID, nextIDDirect)
      thisGraph.add_edge(myID, nextIDIndirect)

  return thisTopology


# For folded torus type L1 topology
def folded_torus_head_gen(n,m):
  thisClass = 'F'
  thisParams = (n, m)
  thisGraph = nx.Graph();
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph);

  def genID(i, j):
    return str(i) + DELIMITER + str(j)

  #Add nodes
  for i in range(n):
    for j in range(m):
      genInner(genID(i, j))
      cnode = getHeadNode(genID(i, j))
      thisGraph.add_node(genID(i, j), exdata=cnode)

  def safeAddEdge(isrc, jsrc, idest, jdest):
    idest = (idest + n) % n
    jdest = (jdest + m) % m

    srcID = genID(isrc, jsrc)
    destID = genID(idest, jdest)
    thisGraph.add_edge(srcID, destID)

  #Add edges in columns
  for j in range(m):
    #Add link to immediately next of first node
    safeAddEdge(0, j, 1, j)
    #Add links in internal nodes
    for i in range(int(n / 2) - 1):
      safeAddEdge(2*i, j, 2*i+2, j)
      safeAddEdge(2*i+1, j, 2*i+3, j)
    #Add link to prev of last node
    safeAddEdge(n-1, j, n-2, j)
  
  #Add edges in rows
  for i in range(n):
    #Add link to immediately next of first node
    safeAddEdge(i, 0, i, 1)
    #Add links in internal nodes
    for j in range(int(m / 2) - 1):
      safeAddEdge(i, 2*j, i, 2*j+2)
      safeAddEdge(i, 2*j+1, i, 2*j+3)
    #Add link to prev of last node
    safeAddEdge(i, m-1, i, m-2)

  return thisTopology



## Function to print the network.dot file
def print_func():
  nx.drawing.nx_pydot.write_dot(outerTopology.topoGraph, "Network.Outer.dot")
  for q in innerTopologies:
    nx.drawing.nx_pydot.write_dot(innerTopologies[q].topoGraph, "Network." + q + ".dot")



### Start of parsing ###

# Assign values from the L1 topology
L1_network_type, L1_n, L1_m = L1.split(",")
L1_n = int(L1_n)
L1_m = int(L1_m)

if L1_network_type == "R":
  outerTopology = ring_head_gen(L1_n)    
elif L1_network_type == "C":
  outerTopology = chain_head_gen(L1_n)
elif L1_network_type == "M":
  outerTopology = mesh_head_gen(L1_n,L1_m)
elif L1_network_type == "B":
  outerTopology = butterfly_head_gen(L1_n)
elif L1_network_type == "F":
  outerTopology = folded_torus_head_gen(L1_n,L1_m)
elif L1_network_type == "H":
  outerTopology = hypercube_head_gen()

print_func()

def getTopo(id, inner:bool):
  if(outerTopology.topoGraph.nodes.get(id) != None):
    return outerTopology.topoGraph.nodes[id]
  for q in innerTopologies:
    if(innerTopologies[q].topoGraph.nodes.get(id) != None):
      return innerTopologies[q].topoGraph.nodes[id]
  return None

def getNode(id):
  if(outerTopology.topoGraph.nodes.get(id) != None):
    return outerTopology.topoGraph.nodes[id]
  for q in innerTopologies:
    if(innerTopologies[q].topoGraph.nodes.get(id) != None):
      return innerTopologies[q].topoGraph.nodes[id]
  return None

# returns nextID, vcID
def route_mesh(src:Node, dest:Node, outside:bool):
  idsrc = src.headID if outside else src.inID
  iddest = dest.headID if outside else dest.inID

  isrc, jsrc = list(map(lambda x : int(x), idsrc.split(DELIMITER)))
  idest, jdest = list(map(lambda x : int(x), iddest.split(DELIMITER)))

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)
  if(isrc < idest):
    isrc += 1
  elif(jsrc < jdest):
    jsrc += 1
    vcid += 1
  elif(isrc > idest):
    isrc -= 1
    vcid += 2
  else:
    jsrc -= 1
    vcid += 3

  if(outside):
    nextid = innerTopologies[str(isrc) + DELIMITER + str(jsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
  
  return nextid, str(vcid)

def route_folded_torus(src:Node, dest:Node, outside:bool):
  idsrc = src.headID if outside else src.inID
  iddest = dest.headID if outside else dest.inID

  isrc, jsrc = list(map(lambda x : int(x), idsrc.split(DELIMITER)))
  idest, jdest = list(map(lambda x : int(x), iddest.split(DELIMITER)))

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)

  n, m = srcTopo.topoParams
  if(isrc < idest):
    if(idest - isrc > (isrc + n - idest)):
      isrc -= 1; vcid += 2
    else:
      isrc += 1
  elif(jsrc < jdest):
    if(jdest - jsrc > (jsrc + m - jdest)):
      jsrc -= 1; vcid += 3
    else:
      jsrc += 1; vcid += 1
  elif(isrc > idest):
    if(isrc - idest > (idest + n - isrc)):
      isrc += 1
    else:
      isrc -= 1; vcid += 2
  else:
    if(jsrc - jdest > (jdest + n - jsrc)):
      jsrc += 1; vcid += 1
    else:
      jsrc -= 1; vcid += 3

  if(isrc < 0):
    isrc = n - 1
  elif(isrc == n):
    isrc = 0
  
  if(jsrc < 0):
    jsrc = m - 1
  elif(jsrc == m):
    jsrc = 0

  if(outside):
    nextid = innerTopologies[str(isrc) + DELIMITER + str(jsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
  
  return nextid, str(vcid)

def route_chain(src:Node, dest:Node, outside:bool):
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)

  if(idsrc < iddest):
    idsrc += 1
  else:
    idsrc -= 1; vcid += 1

  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)

def route_ring(src:Node, dest:Node, outside:bool):
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)

  n = srcTopo.topoParams

  if(idsrc < iddest):
    if(iddest - idsrc > (idsrc + n - iddest)):
      idsrc -= 1; vcid += 1
    else:
      idsrc += 1
  else:
    if(idsrc - iddest > (iddest + n - idsrc)):
      idsrc += 1
    else:
      idsrc -= 1; vcid += 1
  
  if(idsrc < 0):
    idsrc = n - 1
  elif(idsrc == n):
    idsrc = 0

  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)

def route_butterfly(src:Node, dest:Node, outside:bool):

  #This function also prints the switches intermediate directly
  
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)

  n = srcTopo.topoParams

  def prevSwitch(current, stage):
    bit = 1 << (stage - 2)
    return bit ^ current


  if (idsrc < iddest):    # Left to right routing. Assuming there are no illegal routings due to invalid inputs  

    current_switch = int(idsrc/2)
    final_switch = int((int(iddest) - n/2 )/2)       

    if (outside):
      print("Node (Switch): {}, VC : {}",.format{Node.generateID(True, str(1) + DELIMITER + str(current_switch), 'B', '', True),vcid})    
    else:
      print("Node (Switch): {}, VC : {}",.format{Node.generateID(False, src.headID, src.inClass, str(1) + DELIMITER + str(current_switch), True),vcid})    
      
    for i in range(2,int(log2(n))):
      if current_switch %(2^i) == final_switch %(2^i):
        next_switch = current_switch
      else :
        next_switch = nextSwitch(current_switch,i)
       
      if (outside):
        print("Node (Switch): {}, VC : {}",.format{Node.generateID(True, str(i) + DELIMITER + str(next_switch), 'B', '', True),vcid})   #Printing internal VC 
      else :
        print("Node (Switch): {}, VC : {}",.format{Node.generateID(False, src.headID, src.inClass, str(i) + DELIMITER + str(next_switch), True),vcid})   #Printing internal VC 

      current_switch = next_switch


  else :   #Routing from right to left

    current_switch = int((idsrc) - n/2 )/2)
    final_switch = int(iddest/2)

    if (outside):
      print("Node (Switch): {}, VC : {}",.format{Node.generateID(True, str(1) + DELIMITER + str(current_switch), 'B', '', True),vcid})    
    else:
      print("Node (Switch): {}, VC : {}",.format{Node.generateID(False, src.headID, src.inClass, str(1) + DELIMITER + str(current_switch), True),vcid})    
      
    for i in range(int(log2(n))-1,1,-1):
      if current_switch %(2^i) = final_switch %(2^i):
        next_switch = current_switch
      else :
        next_switch = prevSwitch(current_switch,i)

      if (outside):
        print("Node (Switch): {}, VC : {}",.format{Node.generateID(True, str(i) + DELIMITER + str(next_switch), 'B', '', True),vcid})   #Printing internal VC 
      else :
        print("Node (Switch): {}, VC : {}",.format{Node.generateID(False, src.headID, src.inClass, str(i) + DELIMITER + str(next_switch), True),vcid})   #Printing internal VC 

      current_switch = next_switch

  if(outside):
      nextid = innerTopologies[str(iddest)].headID
  else:
      nextid = Node.generateID(False, src.headID, src.inClass, str(idest))
      if(srcTopo.topoGraph.nodes.get(nextid) == None):
          nextid = Node.generateID(True, src.headID, src.inClass, str(idest))

            
  return nextid, str(vcid)

def route_hypercube(src:Node, dest:Node, outside:bool):
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcid = 4*int(src.isHead)
  
  if((idsrc & 0b100) != (iddest & 0b100)):
    idsrc ^= 0b100
  elif((idsrc & 0b100) != (iddest & 0b100)):
    idsrc ^= 0b010
    vcid += 1
  else:
    idsrc ^= 0b001
    vcid += 2

  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)

def route_backend(src:Node, dest:Node, outer:bool):
  routingClass = src.inClass
  if(outer):
    routingClass = outerTopology.topoClass
  
  if(routingClass == 'C'):
    return route_chain(src, dest, outer)
  elif(routingClass == 'R'):
    return route_ring(src, dest, outer)
  elif(routingClass == 'B'):
    return route_butterfly(src, dest, outer)
  elif(routingClass == 'F'):
    return route_folded_torus(src, dest, outer)
  elif(routingClass == 'H'):
    return route_hypercube(src, dest, outer)
  elif(routingClass == 'M'):
    return route_mesh(src, dest, outer)

  print("routing class not found")
  exit()

def route_inside(src:Node, dest:Node):
  return route_backend(src, dest, False)

def route_outside(src:Node, dest:Node):
  return route_backend(src, dest, True)

#Replace destination with the tile's head node
def route_outwards(src:Node, dest:Node):
  dest = innerTopologies[src.headID].topoGraph.nodes[innerTopologies[src.headID].headID]['exdata']
  return route_backend(src, dest, False)

def route(idsrc, iddest):
  nodesrc = getNode(idsrc)['exdata']
  nodedest = getNode(iddest)['exdata']
  tilesrc = nodesrc.headID
  tiledest = nodedest.headID
  
  #This case: since we're passed unequal src, dest with same head,
  #           route them within a tile
  if(tilesrc == tiledest):
    return route_inside(nodesrc, nodedest)

  #If src is a Head, and heads of tiles differ, route src outside
  if(nodesrc.isHead):
    return route_outside(nodesrc, nodedest)
  
  #If src is not a Head, route it to the head of its tile
  return route_outwards(nodesrc, nodedest)


def simulateOnce():
  print("Enter source ID (or EXIT to stop): ", end='')
  sourceID = input()
  if(sourceID == "EXIT"):
    print("\nQuitting...")
    exit()
  print("\nEnter destination ID: ", end='')
  destID = input()

  print("\nRouting...\n")

  while(sourceID != destID):
    nextID, vcID = route(sourceID, destID)
    print("Node: " + nextID + ", VC: " + vcID)
    sourceID = nextID

  print("\nRouting complete.\n")

while True:
  simulateOnce()
