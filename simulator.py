#!/usr/bin/python
# monolithic simulator

### Network on Chip - Project - 2
### Simulating transfer of a flit in a two level network of nodes
### Authors : Shashank Nag (EE19B118), Vedaant Alok Arya (CS19B046), Pole Praneeth
### ----------------------------------------------------------------
### INPUT:
### L1Topology.txt will have single line with this data
### X,n,m where X = C, R, M, F, H, B
### C: Chain, R: Ring, M: Mesh, F: Folded Torus, H: Hypercube of dimension 3 (8 nodes), B: Butterfly network
### n: Number of nodes in first dimension
### m: Number of nodes in second dimension - it is 1 for C and R.
### n = m = 3 for H and 
### n = m = 2^k  (Power of 2) for B for some k > 1
###
### L2Topology.txt will have n X m lines with each line as the same syntax as above.
###
### The simulator runs as an Interactive application.
### ----------------------------------------------------------------
### OUTPUT:
### Network.Outer.dot - a DOT format file containing graphical representation of outer topology
### Network.<headID>.dot - a DOT format file for each inner topology's graph
###
### The simulator will output the routing in the format:
### Node <(Switch)>?: <NodeID>, VC: <VCID>
### For as many nodes as are encountered while routing.
###
### The Node IDs are defined in the respective *inner* DOT files.
### Note for outer nodes (Head nodes), the ID is not as indicated in the Outer DOT file,
### it is the ID in corresponding inner DOT file, the one which starts with "O" (Outer)
### Non-head IDs start with "I".
### -----------------------------------------------------------------
### DEPENDENCIES:
### networkx, pydot - for graph representation and DOT file generation respectively
### -----------------------------------------------------------------
### CONVENTION FOR NODE IDS:
###   if connects to outside network
###      O<outID><DELIMITER><inID>
###      binary encoding: 1 <outID bits> <inID bits>
###      example: outside max nodes = 16, inside max nodes = 16
###      1 oooo z iiii
###      1 0101   0011
###   else
###      I<outID><DELIMITER><inID>
###      binary encoding: 0 <outID bits> <inID bits>
###      example: continued
###      0 0000   0010
### 
### Switches are given IDs but not treated as Nodes when routing
### The switches are implemented as psuedo nodes, 
###   in the sense that they are essentially a set of MUXes which are enabled by the scheduler
### inID and outID are tuples of integers (in mesh, butterfly, foldedtorus)
### -----------------------------------------------------------------


###################
####  IMPORTS  ####
###################

# log2 used for calculating stage count in butterfly network
from math import log2
# pydot is imported by nx when calling its dot output function
import networkx as nx




##############################
####  SUPPORTING CLASSES  ####
##############################

# Class which stores extra data for a Node
# - generateID: generates an ID for a node, given the parameters
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

# Class which stores data about a topology
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




###################
####  GLOBALS  ####
###################

# This object stores the outer topology
outerTopology = {}
# This dictionary stores inner topology objects
innerTopologies = {}
# The delimiter in string IDs
DELIMITER = 'Z'
# The input files
file1 = open(r"L1Topology.txt","r")  
file2 = open(r"L2Topology.txt","r")




##############################################
####  INNER TOPOLOGY GENERATOR FUNCTIONS  ####
##############################################

# Function to generate the tile for a chain type L2 connection
# n is the length of the chain
# id is the head id for this tile - note this is not the actual id for the head node
def chain_gen(n, id):
  # Create topology object
  thisClass = 'C'
  thisParams = (n, )
  thisGraph = nx.Graph();
  # In order: not outer topology, no head node id defined, class is thisClass,
  #           params are thisParams, graph representation is thisGraph
  thisTopology = Topology(False, '', thisClass, thisParams, thisGraph);

  # Trivial case of one node. It isn't connected to anything
  if n == 1:
    # Special case of an ID: this node has a blank innerID 
    node = Node(True, id, thisClass, '')
    # Add node to topology's graph rep
    thisGraph.add_node(node.id, exdata=node)
    # Set this node as the head node
    thisTopology.headID = node.id
  else :
    # Add nodes
    for i in range(0, n):
      isHead = False
      # If we encounter a head node
      if(i == int(n/2)):
        isHead = True
        thisTopology.headID = Node.generateID(True, id, thisClass, str(i))

      # Generate a node
      cnode = Node(isHead, id, thisClass, str(i))
      # Add it
      thisGraph.add_node(cnode.id, exdata=cnode)

    # Add edges between nodes
    for i in range(0, n-1):
      # Generate IDs for current and immediately next node
      myID = Node.generateID((i == int(n/2)), id, thisClass, str(i))
      nextID = Node.generateID(((i+1) == int(n/2)), id, thisClass, str(i+1))

      # Add an undirected link (nx.Graph() is undirected)
      thisGraph.add_edge(myID, nextID)

  # Add this topology to the innerTopologies dict
  innerTopologies[id] = thisTopology


# Function to generate the tile for a ring type L2 connection
# n is the length of the ring
# id is the head id for this tile
def ring_gen(n, id):
  # Create topology object
  thisClass = 'R'
  thisParams = (n, )
  thisGraph = nx.Graph()
  thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph)
  
  # Trivial case of one node
  if n == 1:
    node = Node(True, id, thisClass, '')
    thisGraph.add_node(node.id, exdata=node)
    thisTopology.headID = node.id

  # Ring with only two nodes. The nodes are connected to each other
  if n == 2:
    # Generate and add the two nodes
    node1 = Node(False, id, thisClass, '0')
    node2 = Node(True, id, thisClass, '1')
    thisGraph.add_node(node1.id, exdata=node1)
    thisGraph.add_node(node2.id, exdata=node2)
    # Set head in topology object, as latter node
    thisTopology.headID = node2.id
    # Link them
    thisGraph.add_edge(node1.id, node2.id)

  # Non trivial case
  else :
    # Adding nodes, part 1: headnode
    headnode = Node(True, id, thisClass, '0')
    thisGraph.add_node(headnode.id, exdata=headnode)
    thisTopology.headID = headnode.id
    # Adding nodes, part 2: others
    for i in range(1, n):
      cnode = Node(False, id, thisClass, str(i))
      thisGraph.add_node(cnode.id, exdata=cnode)

    # Adding links except to head
    for i in range(1, n-1):
      myID = Node.generateID(False, id, thisClass, str(i))
      nextID = Node.generateID(False, id, thisClass, str(i + 1))
      thisGraph.add_edge(myID, nextID)

    # Adding links to head
    thisGraph.add_edge(headnode.id, Node.generateID(False, id, thisClass, str(n-1)))
    thisGraph.add_edge(headnode.id, Node.generateID(False, id, thisClass, str(1)))

  # Add this topology to inner topologies dict
  innerTopologies[id] = thisTopology


# Function to generate the tile for a hypercube type L2 connection
# Dimension is forced as 3 (8 nodes)
# id is head id for the tile
def hypercube_gen(id):
    thisClass = 'H'
    thisParams = None
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);
    
    # Create and add nodes
    nodes = [Node(True, id, thisClass, '0')]
    thisGraph.add_node(nodes[0].id, exdata=nodes[0])
    thisTopology.headID = nodes[0].id

    for i in range(1, 8):
      nodes.append(Node(False, id, thisClass, str(i)))
      thisGraph.add_node(nodes[i].id, exdata=nodes[i])

    # Now add links
    for i in range(8):
      # Edges are made by inverting 1 bit in each position
      # 3 edges for our 3d hypercube
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 1].id)
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 2].id)
      thisGraph.add_edge(nodes[i].id, nodes[i ^ 4].id)

    # Add inner topology to dict
    innerTopologies[id] = thisTopology


# Function to generate the tile for a mesh type L2 connection
# Dimension of n x m (n rows and m columns)
# id is head id for the tile
def mesh_gen(n, m, id):
    thisClass = 'M'
    thisParams = (n, m)
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

    # Given i, j this function checks if it is a head node according to params
    def checkHead(ix, jx):
      return (ix == int(n/2)) and (jx == (int(m/2)))

    # Add nodes
    for i in range(n): # each row
      for j in range(m): # each column
        # Add node to graph
        isHead = checkHead(i, j)
        cnode = Node(isHead, id, thisClass, str(i) + DELIMITER + str(j))
        thisGraph.add_node(cnode.id, exdata=cnode)

        # If headnode, set topology property
        if(isHead):
          thisTopology.headID = cnode.id

    # Checks if node i, j are valid
    def checkNode(ix, jx):
      if(ix < 0 or jx < 0):
        return False
      if(ix >= n or jx >= m):
        return False
      return True

    # Safely adds edges - if dest node exists, and accounting for headID
    def addEdgeSafe(isrc, jsrc, idest, jdest):
      # If not safe, return
      if(not checkNode(idest, jdest)):
        return
      # Generate IDs for source and destination
      srcID = Node.generateID(checkHead(isrc, jsrc), id, thisClass, str(isrc) + DELIMITER + str(jsrc))
      destID = Node.generateID(checkHead(idest, jdest), id, thisClass, str(idest) + DELIMITER + str(jdest))
      # Add edge between src and dest
      thisGraph.add_edge(srcID, destID)

    # Add edges
    for i in range(n):
      for j in range(m):
        # Add edge top, bottom, left and right. Function will take care of issues
        addEdgeSafe(i, j, i - 1, j)
        addEdgeSafe(i, j, i + 1, j)
        addEdgeSafe(i, j, i, j - 1)
        addEdgeSafe(i, j, i, j + 1)

    # Add topology to dict
    innerTopologies[id] = thisTopology


# Function to generate the tile for a butterfly type L2 connection
# n is the total number of nodes on left and right
# id is the head id for this tile
def butterfly_gen(n, id):
  thisClass = 'B'
  thisParams = (n, )
  thisGraph = nx.Graph();
  thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

  # node internal IDs: <num1> where
  #   num1 identifies the node index
  # switch internal IDs: <num1><DELIMITER><num2> where
  #   num1 identifies the stage in the butterfly
  #   num2 identifies the switch in the stage

  # Add headID (we know where head is)
  thisTopology.headID = Node.generateID(True, id, thisClass, str(0))
  # Check if this node is the head node
  def checkHead(stage, index):
    # We've selected the 0th node as head node
    if(stage == 0 and index == 0):
      return True
    return False

  # n/2 nodes on left, n/2 on right, n/4 switches in each stage
  # hence, log2(n/4) + 1 = log2(n) - 1 layers of switches
  # and 2 layers of nodes, total log2(n) + 1 layers
  n_stages = int(log2(n)) + 1

  # Add nodes
  for i in range(0, n):
    # Stage differs based on i, and index in stage too, send accordingly to checkHead
    cnode = Node(checkHead(0 if i < int(n/2) else n_stages - 1, i % int(n/2)),
                  id, thisClass, str(i))
    thisGraph.add_node(cnode.id, exdata=cnode)

  # Add switches
  for i in range(1, n_stages - 1):
    # n/4 switches in each stage!
    for j in range(int(n/4)):
      # Note the last parameter is essential. We're giving IDs to switches too, but won't consider them as nodes
      cswitch = Node(False, id, thisClass, str(i) + DELIMITER + str(j), True)
      thisGraph.add_node(cswitch.id, exdata=cswitch)
  
  # Add edges from input to first switch layer
  for i in range(0, int(n/2)):
    # Generate IDs of target node and switch
    nodeID = Node.generateID(checkHead(0, i), id, thisClass, str(i))
    switchID = Node.generateID(False, id, thisClass, str(1) + DELIMITER + str(int(i/2)), True)
    thisGraph.add_edge(nodeID, switchID)
  
  # Add edges from last switch layer to output
  for i in range(0, int(n/4)):
    # Generate IDs of target switch and nodes
    switchID = Node.generateID(False, id, thisClass, str(n_stages - 2) + DELIMITER + str(i), True)
    nodeID1 = Node.generateID(False, id, thisClass, str(int(n/2) + (2*i)))
    nodeID2 = Node.generateID(False, id, thisClass, str(int(n/2) + (2*i + 1)))
    
    # Add edges to both nodes from switch
    thisGraph.add_edge(switchID, nodeID1)
    thisGraph.add_edge(switchID, nodeID2)

  # This method returns the switch index for the next layer indirect switch according to current switch
  def nextSwitch(current, stage):
    # Invert one bit according to stage
    bit = 1 << (stage - 1)
    return bit ^ current

  # Add edges between switches in the inner layers
  for i in range(1, n_stages - 2):
    for j in range(0, int(n/4)):
      # This switch's ID
      myID = Node.generateID(False, id, thisClass, str(i) + DELIMITER + str(j), True)
      # Next Switch IDs
      nextIDDirect = Node.generateID(False, id, thisClass, str(i + 1) + DELIMITER + str(j), True)
      nextIDIndirect = Node.generateID(False, id, thisClass, str(i + 1) + DELIMITER + str(nextSwitch(j, i)), True)
      # Adding edges
      thisGraph.add_edge(myID, nextIDDirect)
      thisGraph.add_edge(myID, nextIDIndirect)

  # Add topology to dict
  innerTopologies[id] = thisTopology


# Function to generate the tile for a folded torus type L2 connection
# Dimension of n x m (n rows and m columns)
# id for the head id of this tile
def folded_torus_gen(n, m, id):
  thisClass = 'F'
  thisParams = (n, m)
  thisGraph = nx.Graph();
  thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

  # Node ID: <num1> <DELIM> <num2>
  #   num1 -> row of the node
  #   num2 -> column of the node

  # This function checks if the i, j point to a head
  def checkHead(i, j):
    # Choosing first node as head for this topology
    if(i == 0 and j == 0):
      thisTopology.headID = Node.generateID(True, id, thisClass, '0Z0')
      return True
    return False

  # Add nodes
  for i in range(n):
    for j in range(m):
      cnode = Node(checkHead(i, j), id, thisClass, str(i) + DELIMITER + str(j))
      thisGraph.add_node(cnode.id, exdata=cnode)

  # Safely add an edge between source (i,j) and dest (i,j)
  def safeAddEdge(isrc, jsrc, idest, jdest):
    # Safety: keeping indices within limits
    idest = (idest + n) % n
    jdest = (jdest + m) % m

    # Generate IDs and link the nodes
    srcID = Node.generateID(checkHead(isrc, jsrc), id, thisClass, str(isrc) + DELIMITER + str(jsrc))
    destID = Node.generateID(checkHead(idest, jdest), id, thisClass, str(idest) + DELIMITER + str(jdest))
    thisGraph.add_edge(srcID, destID)

  # Add edges in columns
  for j in range(m):
    # Add link to immediately next of first node
    safeAddEdge(0, j, 1, j)
    # Add links in internal nodes
    for i in range(int(n / 2) - 1):
      safeAddEdge(2*i,   j, 2*i+2, j)
      safeAddEdge(2*i+1, j, 2*i+3, j)
    # Add link to prev of last node
    safeAddEdge(n-1, j, n-2, j)
  
  # Add edges in rows
  for i in range(n):
    # Add link to immediately next of first node
    safeAddEdge(i, 0, i, 1)
    # Add links in internal nodes
    for j in range(int(m / 2) - 1):
      safeAddEdge(i, 2*j, i, 2*j+2)
      safeAddEdge(i, 2*j+1, i, 2*j+3)
    # Add link to prev of last node
    safeAddEdge(i, m-1, i, m-2)

  # Add this topology to dict
  innerTopologies[id] = thisTopology




###########################################
####  OUTER TOPOLOGY HELPER FUNCTIONS  ####
###########################################

# Generates inner topology given the head id
def genInner(id):
  # Read tile info from L2Topology file
  tileInfo = file2.readline()
  # Extract network type, dimensions
  network_type, n, m = tileInfo.split(',')
  n = int(n)
  m = int(m)
  
  # Generate according to network_type
  # Note these generators automatically add the generated Topology object to innerTopologies dict
  # So we can access them right away after genInner is done running
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

# Gets the head node data for the topology with the given head id
def getHeadNode(index):
  srcTopo = innerTopologies[index]
  srcHeadID = srcTopo.headID
  srcHeadNode = srcTopo.topoGraph.nodes[srcHeadID]
  return srcHeadNode['exdata']




##############################################
####  OUTER TOPOLOGY GENERATOR FUNCTIONS  ####
##############################################

# Each generator generates the inner topologies, then uses node data from the head nodes of these
#   in the outer topology graph. They don't generate new nodes, except for Butterfly which generates
#   Node objects for switches (however these aren't treated as nodes).
# These call genInner() for each "node addition" of their own, then fetch the head node for the
#   topology just generated.
# Return values are the outerTopology object

# For ring type L1 topology
def ring_head_gen(n):
  thisClass = 'R'
  thisParams = (n, )
  thisGraph = nx.Graph()
  thisTopology = Topology(True, 0, thisClass, thisParams, thisGraph)

  # Two node chain case
  if n == 2:
    # Generate the topologies
    genInner('0')
    node0 = getHeadNode('0')
    thisGraph.add_node('0', exdata=node0)
    genInner('1')
    node1 = getHeadNode('1')
    thisGraph.add_node('1', exdata=node1)

    # Add edge between them
    thisGraph.add_edge('0', '1')

  # Non-trivial case
  else :
    # Adding nodes
    for i in range(n):
      # Generate each one, get its head node, add it to our graph
      genInner(str(i))
      node = getHeadNode(str(i))
      thisGraph.add_node(str(i), exdata=node)

    # Adding links
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
    # Generate nodes
    for i in range(n):
      genInner(str(i))
      node = getHeadNode(str(i))
      thisGraph.add_node(str(i), exdata=node)

    # Add links
    for i in range(0, n-1):
      thisGraph.add_edge(str(i), str(i+1))

  else:
    # Sanity check
    print("Invalid dimensions for outer topology as chain")
    exit()

  return thisTopology


# For hypercube type L1 topology
def hypercube_head_gen():
  thisClass = 'H'
  thisParams = None
  thisGraph = nx.Graph();
  thisTopology = Topology(True, '', thisClass, thisParams, thisGraph);
  n = 8 # Fixed dimensions for hypercube

  # Generate nodes
  for i in range(n):
    genInner(str(i))
    node = getHeadNode(str(i))
    thisGraph.add_node(str(i), exdata=node)
  
  # Add links
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

  # This returns the head id given i, j (Note not head node id, that is generated by inner topo generators)
  def genID(ix, jx):
    return str(ix) + DELIMITER + str(jx)

  # Generate nodes
  for i in range(n):
    for j in range(m):
      genInner(genID(i, j))
      node = getHeadNode(genID(i, j))
      thisGraph.add_node(genID(i, j), exdata=node)

  # Checks if node i, j are valid
  def checkNode(ix, jx):
    if(ix < 0 or jx < 0):
      return False
    if(ix >= n or jx >= m):
      return False
    return True

  # Safely add an edge, just like in mesh_gen
  def addEdgeSafe(isrc, jsrc, idest, jdest):
    if(not checkNode(idest, jdest)):
      return
    thisGraph.add_edge(genID(isrc, jsrc), genID(idest, jdest))

  # Add edges
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

  # Number of stages, like in butterfly_gen
  n_stages = int(log2(n)) + 1

  # Generate nodes only
  for i in range(0,n):
    genInner(str(i))
    cnode = getHeadNode(str(i))
    thisGraph.add_node(str(i), exdata=cnode)

  # Returns an ID of a switch, given stage and index
  # switch names: <num1> <DELIM> <num2> :
  #   num1 identifies the stage in the butterfly
  #   num2 identifies the switch in the stage
  def switchID(stage, index):
    return str(stage) + DELIMITER + str(index)

  # Generate switches (Note creates Node objects)
  for i in range(1, n_stages - 1):
    for j in range(0, int(n/4)):
      thisGraph.add_node(str(i), exdata=Node(True, switchID(i, j), thisClass, '', True))
  
  # Add edges from input to first switch layer
  for i in range(0, int(n/2)):
    myID = Node.generateID(True, switchID(1, int(i/2)), thisClass, '', True)
    thisGraph.add_edge(str(i), myID)
  
  # Add edges from last switch layer to output
  for i in range(0, int(n/4)):
    myID = Node.generateID(True, switchID(n_stages - 2, i), thisClass, '', True)
    nodeID1 = str(int(n/2) + 2*i)
    nodeID2 = str(int(n/2) + 2*i + 1)
    
    thisGraph.add_edge(myID, nodeID1)
    thisGraph.add_edge(myID, nodeID2)

  # Returns index of next stage indirect switch connected to given switch
  def nextSwitch(current, stage):
    bit = 1 << (stage - 1)
    return bit ^ current

  # Add edges between switches in the inner layers
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

  # Given i,j return ID of node
  def genID(i, j):
    return str(i) + DELIMITER + str(j)

  # Add nodes
  for i in range(n):
    for j in range(m):
      genInner(genID(i, j))
      cnode = getHeadNode(genID(i, j))
      thisGraph.add_node(genID(i, j), exdata=cnode)

  # Safely add edge, like in folded_torus_gen
  def safeAddEdge(isrc, jsrc, idest, jdest):
    idest = (idest + n) % n
    jdest = (jdest + m) % m

    srcID = genID(isrc, jsrc)
    destID = genID(idest, jdest)
    thisGraph.add_edge(srcID, destID)

  # Add edges in columns
  for j in range(m):
    # Add link to immediately next of first node
    safeAddEdge(0, j, 1, j)
    # Add links in internal nodes
    for i in range(int(n / 2) - 1):
      safeAddEdge(2*i, j, 2*i+2, j)
      safeAddEdge(2*i+1, j, 2*i+3, j)
    # Add link to prev of last node
    safeAddEdge(n-1, j, n-2, j)
  
  # Add edges in rows
  for i in range(n):
    # Add link to immediately next of first node
    safeAddEdge(i, 0, i, 1)
    # Add links in internal nodes
    for j in range(int(m / 2) - 1):
      safeAddEdge(i, 2*j, i, 2*j+2)
      safeAddEdge(i, 2*j+1, i, 2*j+3)
    # Add link to prev of last node
    safeAddEdge(i, m-1, i, m-2)

  return thisTopology




###########################
####  OUTPUT FUNCTION  ####
###########################

## Function to print the network.dot file
def print_func():
  nx.drawing.nx_pydot.write_dot(outerTopology.topoGraph, "Network.Outer.dot")
  for q in innerTopologies:
    nx.drawing.nx_pydot.write_dot(innerTopologies[q].topoGraph, "Network." + q + ".dot")




#########################################
####  NETWORK GENERATION INITIATION  ####
#########################################

# Read the L1 topology file to find the top layer topology
L1 = file1.read()
# Extract values from the L1 topology
L1_network_type, L1_n, L1_m = L1.split(",")
L1_n = int(L1_n)
L1_m = int(L1_m)

# Generate head according to type
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

# Output the DOT files for the generated network
print_func()




####################################
####  ROUTING HELPER FUNCTIONS  ####
####################################

# Get a Node object from any topology given its id
def getNode(id):
  if(outerTopology.topoGraph.nodes.get(id) != None):
    return outerTopology.topoGraph.nodes[id]
  for q in innerTopologies:
    if(innerTopologies[q].topoGraph.nodes.get(id) != None):
      return innerTopologies[q].topoGraph.nodes[id]
  return None




#############################
####  ROUTING FUNCTIONS  ####
#############################

# Routing functions work in a tick-based fashion. When called, they route a flit once.
# Butterfly routing function does printing itself, for switches, considering practically they aren't treated as nodes

# Route a flit from src to dest, with src having received it in vcid, and routing done in (outside?outer:inner) topology.
# Mesh routing
def route_mesh(src:Node, dest:Node, outside:bool, vcid=''):
  # Get ID according to routing being done outside or in
  # inID for a node doesn't have its headID or isHead components, which its id does
  idsrc = src.headID if outside else src.inID
  iddest = dest.headID if outside else dest.inID

  # i,j's for src, dest, found from IDs
  isrc, jsrc = list(map(lambda x : int(x), idsrc.split(DELIMITER)))
  idest, jdest = list(map(lambda x : int(x), iddest.split(DELIMITER)))

  # Topology object of the source node
  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  # nextid, vcid will be returned
  nextid = ''
  # H indicates a VC of a head node, being used for outer routing
  vcid = 'H0' if outside else '0'
  
  # X routing
  if(jsrc < jdest):
    jsrc += 1 # move closer to destination j
  elif(jsrc > jdest):
    jsrc -= 1
  # These statements checked if jsrc == jdest, hence X-Y routing
  elif(isrc < idest):
    isrc += 1
  else:
    isrc -= 1

  # Determining nextID according to transformed isrc, jsrc
  if(outside):
    # If outside, find using innerTopologies' headIDs
    nextid = innerTopologies[str(isrc) + DELIMITER + str(jsrc)].headID
  else:
    # If inside, assume it is not a head node
    nextid = Node.generateID(False, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
    # If not found, our assumption was wrong. It is a head node, set nextID accordingly
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
  
  # Return routed info
  return nextid, str(vcid)

# Folded Torus routing
def route_folded_torus(src:Node, dest:Node, outside:bool, vcid=''):
  # Get IDs
  idsrc = src.headID if outside else src.inID
  iddest = dest.headID if outside else dest.inID

  # Extract location info
  isrc, jsrc = list(map(lambda x : int(x), idsrc.split(DELIMITER)))
  idest, jdest = list(map(lambda x : int(x), iddest.split(DELIMITER)))

  # Get source topo
  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  # vcset: if vcid has been shifted to 1, we don't want it being shifted back to 0
  #        if vcset is true, use vcid as given, else generate a new one
  vcset = False

  # Check if vcid supplied is valid
  if(len(vcid > 0)):
    # Check if it was shifted to 1
    vcset = (vcid[-1] == '1')
    if(vcset):
      # If it was shifted:
      #   do not absorb outer vcid when going into an inner topology from outside
      if((not outside) and vcid[0] == 'H'):
        vcset = False
      #   do not absorb inner vcid when going outside the inner topology
      if((outside) and vcid[0] != 'H'):
        vcset = False
  
  # If vcset is false, initialize vcid
  if(not vcset):
    vcid = 'H' if outside else ''

  # Cache i,j to check later if they changed
  icache, jcache = isrc, jsrc

  # n, m are needed to determine shorter arc
  n, m = srcTopo.topoParams

  # X routing with shortest arc
  if(jsrc < jdest):
    # Inc/Dec according to shortest arc
    if(jdest - jsrc > (jsrc + m - jdest)):
      jsrc -= 1
    else:
      jsrc += 1
  elif(jsrc > jdest):
    if(jsrc - jdest > (jdest + n - jsrc)):
      jsrc += 1
    else:
      jsrc -= 1
  # Dateline routing
  elif(isrc != idest):
    isrc += 1

  # Jumping from start to end of a ring/vice-versa
  if(jsrc < 0):
    jsrc = m - 1
  elif(jsrc == m):
    jsrc = 0

  if(isrc == n):
    isrc = 0

  # Dateline routing: setting vc if not previously set
  if(not vcset):
    if(isrc != icache):
      # If i was changed and is now 0, then change VC
      if(isrc == 0):
        vcid += '1'
      else:
        vcid += '0'
    else:
      vcid += '0'

  # Getting nextID appropriately
  if(outside):
    nextid = innerTopologies[str(isrc) + DELIMITER + str(jsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(isrc) + DELIMITER + str(jsrc))
  
  return nextid, str(vcid)

# Chain routing
def route_chain(src:Node, dest:Node, outside:bool, vcid):
  # Get IDs
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  # Get source topo
  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  # VC's only used directionally here
  nextid = ''
  vcid = 'H' if outside else ''

  # If going right, VC 0, else VC 1
  if(idsrc < iddest):
    idsrc += 1; vcid += '0'
  else:
    idsrc -= 1; vcid += '1'

  # Get nextID
  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)

# Ring routing
def route_ring(src:Node, dest:Node, outside:bool, vcid):
  # Get IDs
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  # Get source topo
  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  vcset = False

  # Similar check for vcset as in folded torus
  if(len(vcid) > 0):
    vcset = (vcid[-1] == '1')
    if(vcset):
      # do not absorb outer vcid when going into an inner topology from outside
      if((not outside) and vcid[0] == 'H'):
        vcset = False
      # do not absorb inner vcid when going outside the inner topology
      if((outside) and vcid[0] != 'H'):
        vcset = False
  
  # Initialize vcid if needed
  if(not vcset):
    vcid = 'H' if outside else ''

  # Needed parameter for routing
  n = srcTopo.topoParams

  # Dateline routing - here just using shortest arc
  if(idsrc != iddest):
    idsrc += 1

  if(idsrc == n):
    idsrc = 0

  # Datelne routing - setting VC to 1 if not already set and crossing 0
  if(not vcset):
    if(idsrc == 0):
      vcid += '1'
    else:
      vcid += '0'

  # Get nextid appropriately
  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)

# Butterfly routing
# Note side-effects: This function also prints the switches intermediate directly
def route_butterfly(src:Node, dest:Node, outside:bool, vcid):
  # Get IDs
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  # Get source topo
  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
    
  n = srcTopo.topoParams

  def nextSwitch(current, stage):
    bit = 1 << (stage - 1)
    return bit ^ current

  def prevSwitch(current, stage):
    bit = 1 << (stage - 2)
    return bit ^ current


  if (idsrc < iddest):    # Left to right routing. Assuming there are no illegal routings due to invalid inputs  

    if (outside):  
        vcid = 'H' + str(idsrc)
    else :
        vcid = str(idsrc)       
        
    current_switch = int(idsrc/2)
    final_switch = int((int(iddest) - n/2 )/2)       

    if (outside):
      print("Node (Switch): {}, VC : {}".format(Node.generateID(True, str(1) + DELIMITER + str(current_switch), 'B', '', True),''))    

    else:
      print("Node (Switch): {}, VC : {}".format(Node.generateID(False, src.headID, src.inClass, str(1) + DELIMITER + str(current_switch), True),''))    
      
    for i in range(2,int(log2(n))):
      if current_switch %(2^i) == final_switch %(2^i):
        next_switch = current_switch
      else :
        next_switch = nextSwitch(current_switch,i)
       
      if (outside):
        print("Node (Switch): {}, VC : {}".format(Node.generateID(True, str(i) + DELIMITER + str(next_switch), 'B', '', True),''))    
      else :
        print("Node (Switch): {}, VC : {}".format(Node.generateID(False, src.headID, src.inClass, str(i) + DELIMITER + str(next_switch), True),''))    

      current_switch = next_switch


  else :   #Routing from right to left

    if (outside):  
        vcid = 'H' + str(idsrc - n/2)
    else :
        vcid = str(idsrc - n/2)           
    
    current_switch = int((idsrc - n/2 )/2)
    final_switch = int(iddest/2)

    if (outside):
      print("Node (Switch): {}, VC : {}".format(Node.generateID(True, str(1) + DELIMITER + str(current_switch), 'B', '', True),''))    
    else:
      print("Node (Switch): {}, VC : {}".format(Node.generateID(False, src.headID, src.inClass, str(1) + DELIMITER + str(current_switch), True),''))    
      
    for i in range(int(log2(n))-1,1,-1):
      if current_switch %(2^i) == final_switch %(2^i):
        next_switch = current_switch
      else :
        next_switch = prevSwitch(current_switch,i)

      if (outside):
        print("Node (Switch): {}, VC : {}".format(Node.generateID(True, str(i) + DELIMITER + str(next_switch), 'B', '', True),''))    
      else :
        print("Node (Switch): {}, VC : {}".format(Node.generateID(False, src.headID, src.inClass, str(i) + DELIMITER + str(next_switch), True),''))   

      current_switch = next_switch

  if(outside):
      nextid = innerTopologies[str(iddest)].headID
  else:
      nextid = Node.generateID(False, src.headID, src.inClass, str(iddest))
      if(srcTopo.topoGraph.nodes.get(nextid) == None):
          nextid = Node.generateID(True, src.headID, src.inClass, str(iddest))

            
  return nextid, str(vcid)

# Hypercube routing
def route_hypercube(src:Node, dest:Node, outside:bool, vcid):
  idsrc = int(src.headID if outside else src.inID)
  iddest = int(dest.headID if outside else dest.inID)

  srcTopo = outerTopology if outside else (innerTopologies[src.headID])

  nextid = ''
  #vcid = 4*int(src.isHead)
  
  if (outside):
    vcid = 'H' + str(idsrc)
  else :
    vcid = str(idsrc)
  
  if((idsrc & 0b100) != (iddest & 0b100)):
    idsrc ^= 0b100
  elif((idsrc & 0b100) != (iddest & 0b100)):
    idsrc ^= 0b010
  else:
    idsrc ^= 0b001

  if(outside):
    nextid = innerTopologies[str(idsrc)].headID
  else:
    nextid = Node.generateID(False, src.headID, src.inClass, str(idsrc))
    if(srcTopo.topoGraph.nodes.get(nextid) == None):
      nextid = Node.generateID(True, src.headID, src.inClass, str(idsrc))
  
  return nextid, str(vcid)



################################################
####  ROUTING SIMULATION SUPPORT FUNCTIONS  ####
################################################

# Common routing backend: routes once through corresponding topology
def route_backend(src:Node, dest:Node, outer:bool, vcid):
  # Find corresponding routingClass
  routingClass = src.inClass
  if(outer):
    # If routing outside, just use outerTopology object
    routingClass = outerTopology.topoClass
  
  # Return nextID, vcID by routing using corresponding routing tick
  if(routingClass == 'C'):
    return route_chain(src, dest, outer, vcid)
  elif(routingClass == 'R'):
    return route_ring(src, dest, outer, vcid)
  elif(routingClass == 'B'):
    return route_butterfly(src, dest, outer, vcid)
  elif(routingClass == 'F'):
    return route_folded_torus(src, dest, outer, vcid)
  elif(routingClass == 'H'):
    return route_hypercube(src, dest, outer, vcid)
  elif(routingClass == 'M'):
    return route_mesh(src, dest, outer, vcid)

  # Shouldn't reach here, sanity check
  print("routing class not found")
  exit()

# Route within a tile only
def route_inside(src:Node, dest:Node, vcid):
  return route_backend(src, dest, False, vcid)

# Route in outer topology (from head node to head node)
def route_outside(src:Node, dest:Node, vcid):
  return route_backend(src, dest, True, vcid)

# Route towards head node of the tile from an inner node
def route_outwards(src:Node, dest:Node, vcid):
  # Replace destination with src's tile's head node
  dest = innerTopologies[src.headID].topoGraph.nodes[innerTopologies[src.headID].headID]['exdata']
  return route_backend(src, dest, False, vcid)




#################################################
####  ROUTING SIMULATION FRONTEND FUNCTIONS  ####
#################################################

# Routing frontend, just routes from some source ID which received flit in VC with vcID, and
# is routing towards a destination ID
def route(idsrc, iddest, vcid):
  # Get the src and dest Node objects
  nodesrc = getNode(idsrc)['exdata']
  nodedest = getNode(iddest)['exdata']
  # Get head IDs for these nodes' tiles
  tilesrc = nodesrc.headID
  tiledest = nodedest.headID
  
  # This case: since we're passed unequal src, dest with same head,
  #            route them within a tile
  if(tilesrc == tiledest):
    return route_inside(nodesrc, nodedest, vcid)

  # If src is a Head, and heads of tiles differ, route src outside
  if(nodesrc.isHead):
    return route_outside(nodesrc, nodedest, vcid)
  
  # If src is not a Head, route it to the head of its tile
  return route_outwards(nodesrc, nodedest, vcid)

# Simulates once. Interacts with the user accordingly.
def simulateOnce():
  # Get the source ID
  # User is expected to go through a DOT file to find a favorable source node
  print("Enter source ID (or EXIT to stop): ", end='')
  sourceID = input()

  # Does the user want to exit?
  if(sourceID == "EXIT"):
    return False

  # Get the destination ID
  print("\nEnter destination ID: ", end='')
  destID = input()

  # Sanity check
  if(getNode(sourceID) == None):
    print("\nSource ID not found!")
    return False
  if(getNode(destID) == None):
    print("\nDestination ID not found!")
    return False

  print("\nRouting...\n")

  vcID = ''
  # As described
  while(sourceID != destID):
    # Route once
    nextID, vcID = route(sourceID, destID, vcID)
    # Print received ID, VCID
    print("Node : " + nextID + ", VC : " + vcID)
    # Prepare for next tick
    sourceID = nextID

  print("\nRouting complete.")
  return True




############################
####  BEGIN SIMULATION  ####
############################

INTRO = "Please refer to the generated DOT files (Network.<headID>.dot) to find favorable node IDs.\n"
OUTRO = "\nQuitting..."

print(INTRO)

# Keep simulating. simulateOnce() returns False if the user chooses to exit, or we get an error.
while simulateOnce():
  print("")

print(OUTRO)
exit()