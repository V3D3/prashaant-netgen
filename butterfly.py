#Function to route through a ring network
def butterfly(curr_node, dest_node):

    dest_head = dest_node.ishead

    if dest_node.headID == curr_node.headID :             #Checking if the destination and current node are in the same tile
      internal_dest = dest_node.inID                           #Where we want the tile to route to
      isL1 = 0                                            #Internal routing
      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into internal VC 0

    else :
      if curr_node.isHead == 0 :
        internal_dest = 0  # Head of butterfly network
        isL1 = 0                                                   #Internal routing
        print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into internal VC 0
      
      elif curr_node.isHead == 1 :
        internal_dest = dest_node.headID  # network[dest_ID.outer_id].headnode()
        isL1 = 1
        print("Node ID: {}, Virtual Channel ID : H{}",.format{Node.generateID(curr_node.isHead, curr_node.headID, curr_node.inClass, curr_node.inID),0})   #Flit loaded into global VC  --- check !!!


    butterfly_router(curr_ID,internal_dest,isL1,dest_head)

    
    
def butterfly_router(curr_node,internal_dest,isL1, dest_head):
  
  def prevSwitch(current, stage):
    bit = 1 << (stage - 2)
    return bit ^ current


  vc = 0     #Virtual Channel is always 0 in butterfly network


  if isL1 == 0 :    #Routing within the tile, local network
    N = int(internalTopologies[current_node.headID].topoParams[0])  #N                        

    if  int(curr_node.inID) < int(internal_dest)    # Left to right routing. Assuming there are no illegal routings due to invalid inputs  

      current_switch = int(current_node.inID/2)
      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(False, current_node.headID, current_node.inClass, str(1) + DELIMITER + str(int(current_node.inID/2)), True),vc})   #Printing internal VC 
      final_switch = int((int(internal_dest) - N/2 )/2)       
      
      for i in range(2,int(log2(N))):
        if current_switch %(2^i) = final_switch %(2^i):
          next_switch = current_switch
        else :
          next_switch = nextSwitch(current_switch,i)

        print("Node (Switch) ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(False, current_node.headID, current_node.inClass, str(i) + DELIMITER + next_switch, True),vc})   #Printing internal VC 
        current_switch = next_switch

      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(dest_head, current_node.headID, current_node.inClass, internal_dest, False),vc})   #Printing the final node 


    else :   #Routing from right to left

      current_switch = int((int(current_node.inID) - N/2 )/2)
      final_switch = int(internal_dest/2)

      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(False, current_node.headID, current_node.inClass, str(1) + DELIMITER + str(current_switch), True),vc})   #Printing internal VC 
      
      for i in range(int(log2(N))-1,1,-1):
        if current_switch %(2^i) = final_switch %(2^i):
          next_switch = current_switch
        else :
          next_switch = prevSwitch(current_switch,i)

        print("Node (Switch) ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(False, current_node.headID, current_node.inClass, str(i) + DELIMITER + next_switch, True),vc})   #Printing internal VC 
        current_switch = next_switch

      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(dest_head, current_node.headID, current_node.inClass, internal_dest, False),vc})   #Printing the final node 



  else :    #Routing in L1
    N = int(internalTopologies[current_node.headID].topoParams[0])  #N                        

    if  int(curr_node.inID) < int(internal_dest)    # Left to right routing. Assuming there are no illegal routings due to invalid inputs  

      current_switch = int(current_node.inID/2)
      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(True, str(1) + DELIMITER + str(int(current_node.inID/2)), current_node.inClass, '', True),vc})   #Printing internal VC 
      final_switch = int((int(internal_dest) - N/2 )/2)       
      
      for i in range(2,int(log2(N))):
        if current_switch %(2^i) = final_switch %(2^i):
          next_switch = current_switch
        else :
          next_switch = nextSwitch(current_switch,i)

        print("Node (Switch) ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(True, str(i) + DELIMITER + next_switch, current_node.inClass, '', True),vc})   #Printing internal VC 
        current_switch = next_switch
                                                                                            
      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(True, internal_dest, current_node.inClass, 0, False),vc})   #Printing internal VC 


    else :   #Routing from right to left

      current_switch = int((int(current_node.inID) - N/2 )/2)
      final_switch = int(internal_dest/2)

      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(True, str(1) + DELIMITER + str(current_switch), current_node.inClass, '', True),vc})   #Printing internal VC 
      
      for i in range(int(log2(N))-1,1,-1):
        if current_switch %(2^i) = final_switch %(2^i):
          next_switch = current_switch
        else :
          next_switch = prevSwitch(current_switch,i)

        print("Node (Switch) ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(False, str(i) + DELIMITER + next_switch, current_node.inClass, '', True),vc})   #Printing internal VC 
        current_switch = next_switch

      print("Node ID: {}, Virtual Channel ID : L{}",.format{Node.generateID(True, internal_dest, current_node.inClass, 0, False),vc})   #Printing destination head node





 
