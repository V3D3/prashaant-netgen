#Function to route through a ring network
def ring(curr_node, dest_node):

    if dest_node.headID == curr_node.headID :             #Checking if the destination and current node are in the same tile
      internal_dest = dest_node.inID                           #Where we want the tile to route to
      isL1 = 0                                            #Internal routing
      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into internal VC 0

    else :
      if curr_node.isHead == 0 :
        internal_dest = internalTopologies[curr_node.headID].headID  # network[curr_ID.outer_id].headnode()
        isL1 = 0                                                   #Internal routing
        print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into internal VC 0
      
      elif curr_node.isHead == 1 :
        internal_dest = internalTopologies[dest_node.headID].headID  # network[dest_ID.outer_id].headnode()
        isL1 = 1
        print("Node ID: {}, Virtual Channel ID : H{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into global VC  --- check !!!


    ring_router(curr_ID,internal_dest,isL1)


def ring_router(curr_node,internal_dest,isL1):
  
  current_node = curr_node.copy()
  next_node = current_node.copy()

  if isL1 == 0 :    #Routing within the tile, local network
    N = internalTopologies[current_node.headID].topoParams[0]  #N                        

    if (int(internal_dest) - int(current_node.inID) <= int(N/2) and int(internal_dest) > int(current_node.inID))  or  (int(current_node.inID) - int(internal_dest) >= int(N/2) and int(internal_dest) < int(current_node.inID)) : ## Checking if routing is to be done in increasing order  
      
      vc = 0        #Setting 0th virtual channel
      while current_node.inID != internal_dest :
        next_node.inID = str((int(current_node.internalID)!= N-1) ? int(current_node.internalID) + 1 : 0 )
        if int(current_node.inID) == 0:     #Crossing the date line
          vc = 1
        print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(next_node.isHead, next_node.headID, next_node.inClass, next_node.inID),vc})   #Printing internal VC 
        current_node = next_node.copy()
      
      #return current_node

    else :   #routing in decreasing order

      vc = 0        #Setting 0th virtual channel
      while current_node.inID != internal_dest :
        next_node.inID = str((int(current_node.internalID)!= 0) ? int(current_node.internalID) - 1 : N-1 )
        if current_node.internalID == 1:      #Crossing the date line
          vc = 1
        print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(next_node.isHead, next_node.headID, next_node.inClass, next_node.inID),vc})   #Printing internal VC 
        current_node = next_node.copy()
      
      #return current_node


  else :     # Routing within the L1 topology

    N = outerTopology.topoParams[0]  #N                        
    if (int(internal_dest) - int(current_node.headID) <= int(N/2) and int(internal_dest) > int(current_node.headID))  or  (int(current_node.headID) - int(internal_dest) >= int(N/2) and int(internal_dest) < int(current_node.headID)) : ## Checking if routing is to be done in increasing order  
      
      vc = 0        #Setting 0th virtual channel
      while current_node.headID != internal_dest :
        next_node.headID = str((int(current_node.headID)!= N-1) ? int(current_node.headID) + 1 : 0 )
        if current_node.headID == 0:
          vc = 1
        print("Node ID: {}, Virtual Channel ID : H{}",.format{Node.generateID(True, next_node.headID, innerTopologies[next_node.headID].topoClass, innerTopologies[next_node.headID].headID),vc})   #Printing external VC
        current_node = next_node.copy()
 
    else :   #Routing in decreasing order
      vc = 0        #Setting 0th virtual channel
      while current_node.headID != internal_dest :
        next_node.headID = str((int(current_node.headID)!= 0) ? int(current_node.headID) - 1 : N-1 )
        if current_node.headID == 1:
          vc = 1
        print("Node ID: {}, Virtual Channel ID : H{}",.format{Node.generateID(True, next_node.headID, innerTopologies[next_node.headID].topoClass, innerTopologies[next_node.headID].headID),vc})   #Printing external VC
        current_node = next_node.copy()
 
