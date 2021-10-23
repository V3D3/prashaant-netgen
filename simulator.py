# monolithic simulator
#!/usr/bin/python
#####################################################################################################
#####################################################################################################
### Network on Chip - Project - 2
### Simulating transfer of a flit in a two level network of nodes
### Authors : Vedaant Alok Arya, Pole Praneeth Shashank Nag (EE19B118)
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
        return 'O' + headID + 'Z' + inID
      else:
        return 'I' + headID + 'Z' + inID

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
outerTopology = None
# This dictionary stores inner topology objects
innerTopologies = {}

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
        thisGraph.add_node(node.id, node)
        thisTopology.headID = node.id
    else :
        #Add nodes
        for i in range(0, n):
          isHead = False
          if(i == int(n/2)):
            isHead = True
            thisTopology.headID = Node.generateID(True, id, thisClass, str(i))
          cnode = Node(isHead, id, thisClass, str(i))
          thisGraph.add_node(cnode.id, cnode)

        #Add edges between middle nodes
        for i in range(1, n-1):
          myID = Node.generateID(False, id, thisClass, str(id))

          leftID = Node.generateID(False, id, thisClass, str(i - 1))
          #If this leftID does not exist in there, we're looking at the head node to the left
          if(thisGraph.nodes.get(leftID) == None):
            leftID = Node.generateID(True, id, thisClass, str(i - 1))

          rightID = Node.generateID(False, id, thisClass, str(i + 1))
          #Likewise
          if(thisGraph.nodes.get(leftID) == None):
            rightID = Node.generateID(True, id, thisClass, str(i + 1))

          thisGraph.add_edge(leftID, myID)
          thisGraph.add_edge(rightID, myID)

        #For leftmost node
        leftmostID = Node.generateID(False, id, thisClass, 0)
        #Rightmost ID changes according to it being the head node
        rightID = Node.generateID((int(n/2) == 1), id, thisClass, 1)
        thisGraph.add_edge(leftmostID, rightID)

        #For rightmost node
        rightmostID = Node.generateID((int(n/2) == (n-1)), id, thisClass, n-1)
        leftID = Node.generateID((int(n/2) == (n-2)), id, thisClass, n-2)
        thisGraph.add_edge(rightmostID, leftID)

    #Returning the tile and pointer to head_node
    innerTopologies[id] = thisTopology


# Function to generate the tile for a ring type L2 connection
# n is the length of the ring
def ring_gen(n, id):
    thisClass = 'R'
    thisParams = (n, )
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);
    
    #Trivial case of one node
    if n == 1:
      node = Node(True, id, thisClass, '')
      thisGraph.add_node(node.id, node)
      thisTopology.headID = node.id
    #Ring with only two nodes. The nodes are connected to each other
    if n == 2:
      #Generate and add the two nodes
      node1 = Node(False, id, thisClass, '0')
      node2 = Node(True, id, thisClass, '1')
      thisGraph.add_node(node1.id, node1)
      thisGraph.add_node(node2.id, node2)
      thisTopology.headID = node2.id
      #Link them
      thisGraph.add_edge(node1.id, node2.id)

    #Non trivial case
    else :
      #Adding nodes, P1: headnode
      headnode = Node.generateID(True, id, thisClass, '0')
      thisGraph.add_node(headnode.id, headnode)
      thisTopology.headID = headnode.id
      #Adding nodes, P2: others
      for i in range(1, n):
        cnode = Node(False, id, thisClass, str(i))
        thisGraph.add_node(cnode.id, cnode)

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
    nodes = [Node(True, id, thisClass, 0)]
    thisGraph.add_node(nodes[0].id, nodes[0])

    for i in range(1, 8):
      nodes.append(Node(False, id, thisClass, i))
      thisGraph.add_node(nodes[i].id, nodes[i])

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
def mesh_gen(n,m):
    thisClass = 'M'
    thisParams = (n, m)
    thisGraph = nx.Graph();
    thisTopology = Topology(False, 0, thisClass, thisParams, thisGraph);

    #We need to separately handle the nodes on the perimeter as these have fewer than 4 linkages
   
    ####First Row ####
    #Handling the first node; which is connected only to the one on the right and the one in the next row
    tile.append(["N{}".format(k) for k in [f_nodes + 1,f_nodes + m]])
    ## now do for first row till second last
    for j in range(1, m -1):
      tile.append(["N{}".format(k) for k in [f_nodes + j -1,f_nodes + j + 1, f_nodes + m * 1 + j  ] ])  
    # Now the last node in the first node
    tile.append(["N{}".format(k) for k in [f_nodes + m - 2,f_nodes + m + m -1]])

    ### Second row onwards ####
    for i in range(1, n-1) :
    #then in here, do similarly for first node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i  + 1, f_nodes + m * (i-1) , f_nodes + m * (i+1) ]])
      #For the nodes completely inside
      for j in range(1, m -1):
        tile.append(["N{}".format(k) for k in [f_nodes + m * i + j -1,f_nodes + m * i + j + 1, f_nodes + m * (i-1) + j, f_nodes + m * (i+1) + j  ] ])  
   
      #then in here, do similarly for last node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i + (m-1) -1, f_nodes + m * (i-1) + (m-1), f_nodes + m * (i+1) + (m-1)  ] ])

    ### Last row ####    
    #then do for the last row like the first row
    tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1)  + 1, f_nodes + m * ((n-1)-1)]])    
    for j in range(1, m -1):
      tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1) + j -1,f_nodes + m * (n-1) + j + 1, f_nodes + m * ((n-1)-1) + j  ] ])  

    tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1) + (m-1) -1, f_nodes + m * ((n-1)-1) + (m-1)  ] ])
   


    head_node = f_nodes + int(n/2)*m +  int((m)/2);



    return tile, head_node


def butterfly_gen(f_nodes,n):
    tile = []
    switches = {}

    # switch names: S <num1> w <num2> w <num3> :
    #   num1 identifies the subtopology in which the switch exists
    #   num2 identifies the stage in the butterfly
    #   num3 identifies the switch in the stage

    # add nodes ("Node"s)
    n_stages = int(log2(n))
    # first stage
    for i in range(0,n):
      tile.append(["S{}w{}w{}".format(f_nodes,0,int(i/2))])
    
    head_node = f_nodes + int(n/2)

    # initialize switches in dictionary
    # for each stage
    for k in range(0, n_stages):
      # for each switch in stage
      for i in range(0, int(n / 2)):
        switches['S{}w{}w{}'.format(f_nodes,k,i)] = [];

    # add switches
    for k in range(1, n_stages):
      # each stage has (n/2) switches in our butterfly
      for i in range(0, int(n/2)):
        # current switch is (k-1, i)
        # it should be linked to two switches:
        #   both in the next layer k
        #   first one is to the direct next one,
        #   other one is to one bit flipped, the index of bit is k-1 from LEFT, hence (stages - k) from RIGHT
        switches['S{}w{}w{}'.format(f_nodes,k-1,i)] = ["S{}w{}w{}".format(f_nodes,k,i), "S{}w{}w{}".format(f_nodes,k,(i ^ (2**(n_stages - k - 1))))]

    # last stage (final layer of switches --> output nodes)
    for i in range(0, int(n/2)): # note: n guaranteed to be divisble by 2
      switches['S{}w{}w{}'.format(f_nodes,n_stages-1,i)] = ["N{}".format(f_nodes + n + i*2), "N{}".format(f_nodes + n + i*2 + 1)]
    
    # output nodes are connected to... nothing
    for i in range(0, n):
      tile.append([])

    return tile, head_node, switches

def folded_torus_gen(f_nodes,n,m):

    tile = []

    # The logic for folded torus is that each node is connected to a node which is 2 columns away or 2 rows away. Incase of corner nodes, they are connected to the adjacent nodes
    # Owing to this, we need to handle the nodes running along a boundary of 2 from all sides separately, as these won't have 2 nodes on all its sides 
    ########First Row##################

    #First Node
    tile.append(["N{}".format(k) for k in [f_nodes + 2,f_nodes + 1,f_nodes + m,f_nodes + 2*m]])
    #Second Node
    tile.append(["N{}".format(k) for k in [f_nodes + 1+ 2,f_nodes + 1 - 1,f_nodes + 1+ m,f_nodes + 1 + 2*m]])

    ## now do for first row till last but 2; then do for last node in the first row
    for j in range(2, m -2):
      tile.append(["N{}".format(k) for k in [f_nodes + j -2,f_nodes + j + 2, f_nodes + m * 1 + j,f_nodes + m * 2 + j  ] ])  
    
    #Second last node of first row
    tile.append(["N{}".format(k) for k in [f_nodes + (m - 2)- 2,f_nodes + (m-2)+1,f_nodes + (m-2)+ m,f_nodes + (m-2)+ 2*m]])
    #Last node of first row
    tile.append(["N{}".format(k) for k in [f_nodes + (m - 1)- 2,f_nodes + (m-1)-1,f_nodes + (m-1)+ m,f_nodes + (m-1)+ 2*m]])

    ########Second Row##################

    #First Node
    tile.append(["N{}".format(k) for k in [f_nodes + m + 2,f_nodes + m + 1,f_nodes + m - m,f_nodes + m + 2*m]])
    #Second Node
    tile.append(["N{}".format(k) for k in [f_nodes + (m + 1) + 2,f_nodes + (m+1) - 1,f_nodes + (m+1)- m,f_nodes + (m+1) + 2*m]])

    ## now do for second row till last but 2; then do for last node in the first row
    for j in range(2, m -2):
      tile.append(["N{}".format(k) for k in [f_nodes + (m + j) -2,f_nodes + (m + j) + 2, f_nodes + (m + j) - m * 1 ,f_nodes + (m +j)+ m * 2   ] ])  
    
    #Second last node of second row
    tile.append(["N{}".format(k) for k in [f_nodes + (m + m - 2)- 2,f_nodes + (m + m-2)+1,f_nodes + (m + m-2) - m,f_nodes + (m + m-2)+ 2*m]])
    #Last node of first row
    tile.append(["N{}".format(k) for k in [f_nodes + (m + m - 1)- 2,f_nodes + (m + m-1)-1,f_nodes + (m + m-1) - m,f_nodes + (m + m-1)+ 2*m]])

    ########################################
    ########Other Rows######################

    for i in range(2, n-2) :
    #then in here, do similarly for first node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i  + 2,f_nodes + m * i  + 1, f_nodes + m * (i-2) , f_nodes + m * (i+2) ]])
    #then in here, do similarly for second node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i + 1 + 2,f_nodes + m * i + 1 - 1, f_nodes + m * (i-2) + 1 , f_nodes + m * (i+2) + 1]])

      for j in range(2, m -2):
        tile.append(["N{}".format(k) for k in [f_nodes + m * i + j -2,f_nodes + m * i + j + 2, f_nodes + m * (i-2) + j, f_nodes + m * (i+2) + j  ] ])  
   
      #then in here, do similarly for second last node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i + (m-2) -2,f_nodes + m * i + (m-2) +1, f_nodes + m * (i-2) + (m-2), f_nodes + m * (i+2) + (m-2)  ] ])
      #then in here, do similarly for last node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i + (m-1) -2,f_nodes + m * i + (m-1) -1, f_nodes + m * (i-2) + (m-1), f_nodes + m * (i+2) + (m-1)  ] ])

    ########################################    
    ########Second Last Row##################

    #First Node
    tile.append(["N{}".format(k) for k in [f_nodes + m*(n-2) + 2,f_nodes + m*(n-2) + 1,f_nodes + m*(n-2) + m,f_nodes + m*(n-2) - 2*m]])
    #Second Node
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-2) + 1) + 2,f_nodes + (m*(n-2)+1) - 1,f_nodes + (m*(n-2)+1) + m,f_nodes + (m*(n-2)+1) - 2*m]])

    ## now do for second last row till last but 2; then do for the last 2 nodes in the row
    for j in range(2, m -2):
      tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-2) + j) -2,f_nodes + (m*(n-2) + j) + 2, f_nodes + (m*(n-2) + j) + m * 1 ,f_nodes + (m*(n-2) +j) - 2*m   ] ])  
    
    #Second last node of second last row
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-2) + m - 2)- 2,f_nodes + (m*(n-2) + m-2)+1,f_nodes + (m*(n-2) + m-2) + m,f_nodes + (m*(n-2) + m-2) - 2*m]])
    #Last node of first row
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-2) + m - 1)- 2,f_nodes + (m*(n-2) + m-1)-1,f_nodes + (m*(n-2) + m-1) + m,f_nodes + (m*(n-2) + m-1) - 2*m]])

    ########Last Row##################

    #First Node
    tile.append(["N{}".format(k) for k in [f_nodes + m*(n-1) + 2,f_nodes + m*(n-1) + 1,f_nodes + m*(n-1) - m,f_nodes + m*(n-1) - 2*m]])
    #Second Node
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-1) + 1) + 2,f_nodes + (m*(n-1)+1) - 1,f_nodes + (m*(n-1)+1) - m,f_nodes + (m*(n-1)+1) - 2*m]])

    ## now do for last row till last but 2; then do for the last 2 nodes in the row
    for j in range(2, m -2):
      tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-1) + j) -2,f_nodes + (m*(n-1) + j) + 2, f_nodes + (m*(n-1) + j) - m * 1 ,f_nodes + (m*(n-1) +j) - 2*m   ] ])  
    
    #Second last node of last row
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-1) + m - 2)- 2,f_nodes + (m*(n-1) + m-2)+1,f_nodes + (m*(n-1) + m-2) - m,f_nodes + (m*(n-1) + m-2) - 2*m]])
    #Last node of last row
    tile.append(["N{}".format(k) for k in [f_nodes + (m*(n-1) + m - 1)- 2,f_nodes + (m*(n-1) + m-1)-1,f_nodes + (m*(n-1) + m-1) - m,f_nodes + (m*(n-1) + m-1) - 2*m]])


    head_node = f_nodes + int(n/2)*m +  int((m)/2);

    return tile, head_node


## The following functions handle linkages for the L1 topology. The head nodes are already generated by the corresponding L2 topology functions, and the following functions just add additional head node <-> head node linkages

# For ring type L1 topology
def ring_head_gen(head_nodes,n,final_nodes):


    if n == 2:
        final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[1]) ])
        final_nodes[head_nodes[1]].extend(["N{}".format(head_nodes[0]) ])


    elif n>2 :


        final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [n - 1,1 ] ]) 

        for i in range(1,n-1) :
          final_nodes[head_nodes[i]].extend(["N{}".format(head_nodes[k]) for k in [i-1,i+1 ] ])  

        final_nodes[head_nodes[n-1]].extend(["N{}".format(head_nodes[k]) for k in [ n - 2,0] ])  


# For chain type L1 topology
def chain_head_gen(head_nodes,n,final_nodes):


    if n >= 1:

        final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[1]) ])  

        for i in range(1, n-1) :
            final_nodes[head_nodes[i]].extend(["N{}".format(head_nodes[k]) for k in [i-1, i+1 ] ])  

        final_nodes[head_nodes[n-1]].extend(["N{}".format(head_nodes[n-2])])


# For hypercube type L1 topology
def hypercube_head_gen(head_nodes,final_nodes):


    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [1,3,4 ]])  
    final_nodes[head_nodes[1]].extend(["N{}".format(head_nodes[k]) for k in [0,2,5 ]])  
    final_nodes[head_nodes[2]].extend(["N{}".format(head_nodes[k]) for k in [1,3,6 ]])  
    final_nodes[head_nodes[3]].extend(["N{}".format(head_nodes[k]) for k in [0,2,7 ]])  
    final_nodes[head_nodes[4]].extend(["N{}".format(head_nodes[k]) for k in [0,5,7 ]])  
    final_nodes[head_nodes[5]].extend(["N{}".format(head_nodes[k]) for k in [1,4,6 ]])  
    final_nodes[head_nodes[6]].extend(["N{}".format(head_nodes[k]) for k in [2,5,7 ]])  
    final_nodes[head_nodes[7]].extend(["N{}".format(head_nodes[k]) for k in [3,6,4 ]])  



# For mesh type L1 topology
def mesh_head_gen(head_nodes,n,m,final_nodes):

    if n < 2 or m < 2:
        print("Invalid Mesh dimensions. A mesh of dimension 1 is a chain. Please correct the L2 topology")
        exit()
    

    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [1, m]])
    ## now do for first row till second last; then do for last node in the first row
    for j in range(1, m -1):
      final_nodes[head_nodes[j]].extend(["N{}".format(head_nodes[k]) for k in [j -1,  j + 1, m*1 + j  ] ])  
    
    final_nodes[head_nodes[m-1]].extend(["N{}".format(head_nodes[k]) for k in [ m - 2, m + m -1]])

    for i in range(1, n-1) :
    #then in here, do similarly for first node of the row
      final_nodes[head_nodes[i*m]].extend(["N{}".format(head_nodes[k]) for k in [ m * i  + 1,  m * (i-1) ,  m * (i+1) ]])
      for j in range(1, m -1):
        final_nodes[head_nodes[i*m+j]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + j -1, m * i + j + 1,  m * (i-1) + j,  m * (i+1) + j  ] ])  
   
      #then in here, do similarly for last node of the row
      final_nodes[head_nodes[i*m + m-1 ]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + (m-1) -1,  m * (i-1) + (m-1),  m * (i+1) + (m-1)  ] ])

    #then do for the last row like the first row
    final_nodes[head_nodes[(n-1)*m ]].extend(["N{}".format(head_nodes[k]) for k in [ m * (n-1)  + 1,  m * ((n-1)-1)]])    
    for j in range(1, m -1):
      final_nodes[head_nodes[(n-1)*m + j]].extend(["N{}".format(head_nodes[k]) for k in [ m * (n-1) + j -1, m * (n-1) + j + 1,  m * ((n-1)-1) + j  ] ])  

    final_nodes[head_nodes[(n-1)*m + m - 1 ]].extend(["N{}".format(head_nodes[k]) for k in [ m * (n-1) + (m-1) -1,  m * ((n-1)-1) + (m-1)  ] ])
   


# FOr Butterfly type L1 topology
def butterfly_head_gen(head_nodes,n,final_nodes,final_switches):
    n_stages = int(log2(n))
    for i in range(0,n):
      # add the link to these new switches in the head nodes which will act as input
      final_nodes[head_nodes[i]].extend(["S{}w{}".format(0, int(i/2))])

    # switch names: S <num1> w <num2> :
    #   num1 identifies the stage in the butterfly
    #   num2 identifies the switch in the stage
    # note this automatically differentiates these switches from inner topology switches

    for k in range(0, n_stages):
      for i in range(0, int(n / 2)):
        final_switches['S{}w{}'.format(0,i)] = []

    # add switches
    for k in range(1, n_stages):
      # each stage has (n/2) switches in our butterfly
      for i in range(0, int(n/2)):
        # current switch is (k-1, i)
        # it should be linked to two switches:
        #   both in the next layer k
        #   first one is to the direct next one,
        #   other one is to one bit flipped, the index of bit is k-1 from LEFT, hence (stages - k - 1) from RIGHT
        final_switches['S{}w{}'.format(k-1,i)] = ["S{}w{}".format(k,i), "S{}w{}".format(k,(i ^ (2**(n_stages - k - 1))))]

    # last stage (final layer of switches --> output nodes)
    for i in range(0, int(n/2)): # note: n guaranteed to be divisble by 2
      final_switches['S{}w{}'.format(n_stages-1,i)] = ["N{}".format(head_nodes[n + i*2]), "N{}".format(head_nodes[n + i*2 + 1])]
    
# For folded torus type L1 topology
def folded_torus_head_gen(head_nodes,n,m,final_nodes):

    ########First Row##################

    #First Node
    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [ 2, 1, m, 2*m]])
    #Second Node
    final_nodes[head_nodes[1]].extend(["N{}".format(head_nodes[k]) for k in [ 1+ 2, 1 - 1, 1+ m, 1 + 2*m]])

    ## now do for first row till last but 2; then do for last node in the first row
    for j in range(2, m -2):
      final_nodes[head_nodes[j]].extend(["N{}".format(head_nodes[k]) for k in [ j -2, j + 2,  m * 1 + j, m * 2 + j  ] ])  
    
    #Second last node of first row
    final_nodes[head_nodes[m-2]].extend(["N{}".format(head_nodes[k]) for k in [ (m - 2)- 2, (m-2)+1, (m-2)+ m, (m-2)+ 2*m]])
    #Last node of first row
    final_nodes[head_nodes[m-1]].extend(["N{}".format(head_nodes[k]) for k in [ (m - 1)- 2, (m-1)-1, (m-1)+ m, (m-1)+ 2*m]])

    ########Second Row##################

    #First Node
    final_nodes[head_nodes[m]].extend(["N{}".format(head_nodes[k]) for k in [ m + 2, m + 1, m - m, m + 2*m]])
    #Second Node
    final_nodes[head_nodes[m+1]].extend(["N{}".format(head_nodes[k]) for k in [ (m + 1) + 2, (m+1) - 1, (m+1)- m, (m+1) + 2*m]])

    ## now do for second row till last but 2; then do for last node in the first row
    for j in range(2, m -2):
      final_nodes[head_nodes[m+j]].extend(["N{}".format(head_nodes[k]) for k in [ (m + j) -2, (m + j) + 2,  (m + j) - m * 1 , (m +j)+ m * 2   ] ])  
    
    #Second last node of second row
    final_nodes[head_nodes[m+m-2]].extend(["N{}".format(head_nodes[k]) for k in [ (m + m - 2)- 2, (m + m-2)+1, (m + m-2) - m, (m + m-2)+ 2*m]])
    #Last node of first row
    final_nodes[head_nodes[m+m-1]].extend(["N{}".format(head_nodes[k]) for k in [ (m + m - 1)- 2, (m + m-1)-1, (m + m-1) - m, (m + m-1)+ 2*m]])

    ########################################
    ########Other Rows######################

    for i in range(2, n-2) :
    #then in here, do similarly for first node of the row
      final_nodes[head_nodes[i*m]].extend(["N{}".format(head_nodes[k]) for k in [ m * i  + 2, m * i  + 1,  m * (i-2) ,  m * (i+2) ]])
    #then in here, do similarly for second node of the row
      final_nodes[head_nodes[i*m + 1]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + 1 + 2, m * i + 1 - 1,  m * (i-2) + 1 ,  m * (i+2) + 1]])

      for j in range(2, m -2):
        final_nodes[head_nodes[i*m + j]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + j -2, m * i + j + 2,  m * (i-2) + j,  m * (i+2) + j  ] ])  
   
      #then in here, do similarly for second last node of the row
      final_nodes[head_nodes[i*m + m-2]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + (m-2) -2, m * i + (m-2) +1,  m * (i-2) + (m-2),  m * (i+2) + (m-2)  ] ])
      #then in here, do similarly for last node of the row
      final_nodes[head_nodes[i*m + m-1]].extend(["N{}".format(head_nodes[k]) for k in [ m * i + (m-1) -2, m * i + (m-1) -1,  m * (i-2) + (m-1),  m * (i+2) + (m-1)  ] ])

    ########################################    
    ########Second Last Row##################

    #First Node
    final_nodes[head_nodes[(n-2)*m]].extend(["N{}".format(head_nodes[k]) for k in [ m*(n-2) + 2, m*(n-2) + 1, m*(n-2) + m, m*(n-2) - 2*m]])
    #Second Node
    final_nodes[head_nodes[(n-2)*m + 1]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-2) + 1) + 2, (m*(n-2)+1) - 1, (m*(n-2)+1) + m, (m*(n-2)+1) - 2*m]])

    ## now do for second last row till last but 2; then do for the last 2 nodes in the row
    for j in range(2, m -2):
      final_nodes[head_nodes[(n-2)*m + j]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-2) + j) -2, (m*(n-2) + j) + 2,  (m*(n-2) + j) + m * 1 , (m*(n-2) +j) - 2*m   ] ])  
    
    #Second last node of second last row
    final_nodes[head_nodes[(n-2)*m + m-2]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-2) + m - 2)- 2, (m*(n-2) + m-2)+1, (m*(n-2) + m-2) + m, (m*(n-2) + m-2) - 2*m]])
    #Last node of first row
    final_nodes[head_nodes[(n-2)*m + m-1]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-2) + m - 1)- 2, (m*(n-2) + m-1)-1, (m*(n-2) + m-1) + m, (m*(n-2) + m-1) - 2*m]])

    ########Last Row##################

    #First Node
    final_nodes[head_nodes[(n-1)*m]].extend(["N{}".format(head_nodes[k]) for k in [ m*(n-1) + 2, m*(n-1) + 1, m*(n-1) - m, m*(n-1) - 2*m]])
    #Second Node
    final_nodes[head_nodes[(n-1)*m + 1]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-1) + 1) + 2,(m*(n-1)+1) - 1, (m*(n-1)+1) - m, (m*(n-1)+1) - 2*m]])

    ## now do for last row till last but 2; then do for the last 2 nodes in the row
    for j in range(2, m -2):
      final_nodes[head_nodes[(n-1)*m + j]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-1) + j) -2, (m*(n-1) + j) + 2,  (m*(n-1) + j) - m * 1 , (m*(n-1) +j) - 2*m   ] ])  
    
    #Second last node of last row
    final_nodes[head_nodes[(n-2)*m + m-2]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-1) + m - 2)- 2, (m*(n-1) + m-2)+1, (m*(n-1) + m-2) - m, (m*(n-1) + m-2) - 2*m]])
    #Last node of last row
    final_nodes[head_nodes[(n-1)*m + m-1]].extend(["N{}".format(head_nodes[k]) for k in [ (m*(n-1) + m - 1)- 2, (m*(n-1) + m-1)-1, (m*(n-1) + m-1) - m, (m*(n-1) + m-1) - 2*m]])





## Function to print the network.txt file
def print_func(final_nodes, final_switches):
  file3 = open(r"Network.txt","w")   # Create file to print

  for node_id in range(0,len(final_nodes)):
    print("NodeID: N{}".format(node_id),file=file3)   #Print node id
    print("Links : {}".format(len(final_nodes[node_id])),file=file3) #Print number of links

    for link in range(0,len(final_nodes[node_id])):
      print("L({}):{}".format(link,final_nodes[node_id][link]),file=file3)  #Print each link as per the final_nodes file

  for switch_id in final_switches:
    print("NodeID: {}".format(switch_id), file=file3)
    print("Links : {}".format(len(final_switches[switch_id])), file=file3)

    for link in range(len(final_switches[switch_id])):
      print("L({}):{}".format(link, final_switches[switch_id][link]), file=file3)


### Start of parsing ###

file1 = open(r"L1Topology.txt","r")  
file2 = open(r"L2Topology.txt","r")

L1 = file1.read()        # Read the L1 topology file to find the top layer topology
L2 = file2.readlines()   # Read the L2 topology file and generate a list of network for each tile

# Assign values from the L1 topology
L1_network_type, L1_n, L1_m = L1.split(",")
L1_n = int(L1_n)
L1_m = int(L1_m)

if L1_network_type == "R":
    ring_head_gen(L1_n)
    
elif L1_network_type == "C":
    chain_head_gen(L1_n)
    
elif L1_network_type == "M":
    mesh_head_gen(L1_n,L1_m)
    
elif L1_network_type == "B":
    butterfly_head_gen(L1_n)
    
elif L1_network_type == "F":
    folded_torus_head_gen(L1_n,L1_m)

elif L1_network_type == "H":
    hypercube_head_gen(head_nodes,final_nodes)

#Adding the nodes and linking as per the tiles in L2 topology
for tile_i in L2:

    #Extract the network type and parameters for the tile, and call corresponding functions

  network_type, n, m = tile_i.split(",")
  n = int(n)
  m = int(m)
  f_nodes = len(final_nodes)

  ## The linkages received from the tiles are added extended into the overall final_nodes list
  ## The head node pointers received from each tile is also appended to the head_nodes list
  if network_type == "R":
    tile, head_node = ring_gen(f_nodes,n)  # Ring generator
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "C":
    tile, head_node = chain_gen(f_nodes,n)  # Chain generator
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "M":
    tile, head_node = mesh_gen(f_nodes,n,m) # Mesh generator
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "B":
    tile, head_node, switches = butterfly_gen(f_nodes,n,m) # Butterfly generator
    final_nodes.extend(tile)
    final_switches.update(switches)
    head_nodes.append(head_node)

  elif network_type == "F":
    tile, head_node = folded_torus_gen(f_nodes,n,m)
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "H":
    tile, head_node = hypercube_gen(f_nodes)
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  else :
    print("Invalid network type")



## Calling the functions to Add the head nodes links

