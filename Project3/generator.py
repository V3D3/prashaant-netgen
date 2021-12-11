import re
from math import log2
import networkx as nx

def requirefile(file, user=False):
    try:
        f = open(file)
        out = f.read()
        f.close()
        return out
    except OSError:
        print('Failed to open ' + f)
        if(user):
            print('The file is required as input. Kindly refer to README')
        else:
            print('The file is required for synthesis. This copy of the program is corrupted, kindly obtain a new copy from Team PraShaAnt (Shashank, Vedaant, Praneeth), IIT Madras (CS6230 JN21).')
        exit()

requirefile('core.bsv', True)
requirefile('toplevel_defs.bsv')
requirefile('noc_template_head.bsv')
requirefile('noc_template_tail.bsv')
L1T = requirefile('L1Topology.txt', True)
L2T = requirefile('L2Topology.txt', True)

OUT = ''
OUT += requirefile('noc_template_head.bsv')

####
# Begin parsing the Topologies.
L2T = L2T.split('\n')

def parseTLine(line):
    line = line.split(',')
    return (line[0], int(line[1]), int(line[2]))

L1T = parseTLine(L1T)
L2T = [parseTLine(i) for i in L2T]



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

#########################################
####  NETWORK GENERATION INITIATION  ####
#########################################

# Extract values from the L1 topology
L1_network_type, L1_n, L1_m = L1T

# Generate head according to type
# Utilize generated Topology information, to generate BSV
if L1_network_type == "R":
  outerTopology = ring_head_gen(L1_n)
elif L1_network_type == "C":
  outerTopology = chain_head_gen(L1_n)
elif L1_network_type == "M":
  outerTopology = mesh_head_gen(L1_n, L1_m)
elif L1_network_type == "B":
  outerTopology = butterfly_head_gen(L1_n)
elif L1_network_type == "F":
  outerTopology = folded_torus_head_gen(L1_n, L1_m)
elif L1_network_type == "H":
  outerTopology = hypercube_head_gen()

def mkEdge(G, edge):
    src = edge[2]["src"]
    dest = edge[2]["dest"]
    if (G.nodes[edge[0]]['exdata'].isHead):
        src += 1
    if (G.nodes[edge[1]]['exdata'].isHead):
        dest += 1
    res = f'        mkConnection(n{edge[0]}.node_channels[{src}], n{edge[1]}.node_channels[{dest}]);'
    G.remove_edge(edge[0], edge[1])
    return res

# Add L1 (Head Router) Nodes, and edges among them
G = outerTopology.topoGraph
tc = outerTopology.topoClass

print('[1/3] Adding instantiation of L1 (Head Router) Nodes')

headIdMode = 0
for node in G.nodes:
    # first two fields: n_links (int) and self_addr (Node_addr)
    nodeId = 'n' + node
    if tc == 'R':
        OUT += f'    Ifc_node {nodeId} <- ring_l2({len(G.edges(node))}, {{l1_headID: {int(node)}, l2_ID: 999}});\n'
    elif tc == 'C':
        OUT += f'    Ifc_node {nodeId} <- chain_l2({len(G.edges(node))}, {{l1_headID: {int(node)}, l2_ID: 999}}, {L1_n}, 1, 2, False, True);\n'
    elif tc == 'M':
        headIdMode = 1
        nodeIntId = [int(i) for i in node.split(DELIMITER)]
        nodeIntId = nodeIntId[0] * L1_n + nodeIntId[1]
        OUT += f'Ifc_node {nodeId} <- mesh_l2({len(G.edges(node))}, {{l1_headID: {nodeIntId}, l2_ID: 999}}, {L1_n}, {L1_m}, 1, 2, 3, 4, False, True);\n'
    # elif tc == 'B': # TODO: fix Butterfly (also gens for switches currently)
    #     OUT += f'Ifc_node {nodeId} <- butterfly_l2({}, {{l1_headID: {}, l2_ID: {}}}, {L1_n}, {L1_m}, 1, 2, 3, 4, False, True);\n''
    elif tc == 'F':
        headIdMode = 1
        nodeIntId = [int(i) for i in node.split(DELIMITER)]
        nodeIntId = nodeIntId[0] * L1_n + nodeIntId[1]
        OUT += f'Ifc_node {nodeId} <- folrus_l2({len(G.edges(node))}, {{l1_headID: {nodeIntId}, l2_ID: 999}}, {L1_n}, {L1_m}, 1, 2, 3, 4, False, True);\n'
    elif tc == 'H':
        OUT += f'Ifc_node {nodeId} <- hypercube_l2({len(G.edges(node))}, {{l1_headID: {int(node)}, l2_ID: 999}}, 1, 2, 3, False, True);\n'
    else:
        print('Unknown topology provided in L1Topology.txt: ' + tc)
        exit()
    for edge in G.edges(node):
        OUT += mkEdge(G, edge)

OUT += "\n\n // [2/3] Adding instantiation of L2 Nodes \n\n"
print("[2/3] Adding instantiation of L2 Nodes")

# Add L2 nodes and their edges
for head in innerTopologies:
    T = innerTopologies[head]
    G = T.topoGraph
    tc = T.topoClass

    headIntId = 0
    if (headIdMode == 0):
        headIntId = int(head)
    elif (headIdMode == 1):
        headIntId = [int(i) for i in headIntId.split(DELIMITER)]
        headIntId = headIntId[0] * L1_n + headIntId[1]

    for node in G.nodes:
        nodeId = 'n' + node
        node = G.nodes[node]['exdata'].inID

        if tc == 'R':
            OUT += f'        Ifc_node {nodeId} <- ring_l2({len(G.edges(node))}, {{l1_headID: {int(headIntId)}, l2_ID: {int(node)}}});\n'
        elif tc == 'C':
            OUT += f'        Ifc_node {nodeId} <- chain_l2({len(G.edges(node))}, {{l1_headID: {int(headIntId)}, l2_ID: {int(node)}}}, {L1_n}, 1, 2, {G.nodes[node]["exdata"].isHead}, False);\n'
        elif tc == 'M':
            nodeIntId = [int(i) for i in node.split(DELIMITER)]
            nodeIntId = nodeIntId[0] * T.topoParams[0] + nodeIntId[1]
            OUT += f'        Ifc_node {nodeId} <- mesh_l2({len(G.edges(node))}, {{l1_headID: {int(headIntId)}, l2_ID: {int(nodeIntId)}}}, {L1_n}, {L1_m}, 1, 2, 3, 4, {G.nodes[node]["exdata"].isHead}, False);\n'
        # elif tc == 'B': # TODO: fix Butterfly (also gens for switches currently)
        #     OUT += f'Ifc_node {nodeId} <- butterfly_l2({}, {{l1_headID: {}, l2_ID: {}}}, {L1_n}, {L1_m}, 1, 2, 3, 4, False, True);\n''
        elif tc == 'F':
            nodeIntId = [int(i) for i in node.split(DELIMITER)]
            nodeIntId = nodeIntId[0] * T.topoParams[0] + nodeIntId[1]
            OUT += f'        Ifc_node {nodeId} <- folrus_l2({len(G.edges(node))}, {{l1_headID: {int(headIntId)}, l2_ID: {int(nodeIntId)}}}, {L1_n}, {L1_m}, 1, 2, 3, 4, {G.nodes[node]["exdata"].isHead}, False);\n'
        elif tc == 'H':
            OUT += f'        Ifc_node {nodeId} <- hypercube_l2({len(G.edges(node))}, {{l1_headID: {int(headIntId)}, l2_ID: {int(nodeIntId)}}}, 1, 2, 3, {G.nodes[node]["exdata"].isHead}, False);\n'
        else:
            print('Unknown topology provided in L1Topology.txt: ' + tc)
            exit()

        for edge in G.edges(node):
            OUT += mkEdge(G, edge)

OUT += "\n\n // [3/3] Adding instantiation of cores; linking cores and routers to nodes \n\n";
print("[3/3] Adding instantiation of cores and linking to nodes")

# Instantiate cores and add edges from nodes to cores and routers
for head in innerTopologies:
    G = innerTopologies[head].topoGraph

    for node in G.nodes:
        OUT += f'        Ifc_core c{node} <- mkCore;'
        OUT += f'        mkConnection(c{node}, n{node}.node_channels[0]);'

        if G.nodes[node]["exdata"].isHead:
            OUT += f'        mkConnection(n{head}.node_channels[0], n{node}.node_channels[1]);'

OUT += requirefile('noc_template_tail.bsv')

print('Generation complete. Writing file to disk as "noc.bsv".')
f = open('noc.bsv')
f.write(OUT)
f.close()