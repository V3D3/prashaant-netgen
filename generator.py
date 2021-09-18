#!/usr/bin/python
from math import log2



def chain_gen(f_nodes,n):


    tile = []

    tile.append(["N{}".format(f_nodes + 1) ])  

    for i in range(1, n-1) :
      tile.append(["N{}".format(f_nodes + k) for k in [i-1, i+1 ] ])  

    tile.append(["N{}".format(f_nodes + n-2)])

    head_node = f_nodes + int((n)/2)


    return tile, head_node



def ring_gen(f_nodes,n):

    tile = []

    tile.append(["N{}".format(f_nodes + k) for k in [ n - 1,1 ] ]) 
    for i in range(1,n-1) :
      tile.append(["N{}".format(f_nodes + k) for k in [i-1, i+1 ] ])  

    tile.append(["N{}".format(f_nodes + k) for k in [n - 2,0] ])  


    head_node = f_nodes

    return tile, head_node



def hypercube_gen(f_nodes):

    tile = []

    tile.append(["N{}".format(f_nodes + k) for k in [1,3,4 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [0,2,5 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [1,3,6 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [0,2,7 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [0,5,7 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [1,4,6 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [2,5,7 ]])  
    tile.append(["N{}".format(f_nodes + k) for k in [3,6,4 ]])  

    head_node = f_nodes

    return tile, head_node



def mesh_gen(f_nodes,n,m):

    tile = []

    tile.append(["N{}".format(k) for k in [f_nodes + 1,f_nodes + m]])
    ## now do for first row till second last; then do for last node in the first row
    for j in range(1, m -1):
      tile.append(["N{}".format(k) for k in [f_nodes + j -1,f_nodes + j + 1, f_nodes + m * 1 + j  ] ])  
    
    tile.append(["N{}".format(k) for k in [f_nodes + m - 2,f_nodes + m + m -1]])

    for i in range(1, n-1) :
    #then in here, do similarly for first node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i  + 1, f_nodes + m * (i-1) , f_nodes + m * (i+1) ]])
      for j in range(1, m -1):
        tile.append(["N{}".format(k) for k in [f_nodes + m * i + j -1,f_nodes + m * i + j + 1, f_nodes + m * (i-1) + j, f_nodes + m * (i+1) + j  ] ])  
   
      #then in here, do similarly for last node of the row
      tile.append(["N{}".format(k) for k in [f_nodes + m * i + (m-1) -1, f_nodes + m * (i-1) + (m-1), f_nodes + m * (i+1) + (m-1)  ] ])

    #then do for the last row like the first row
    tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1)  + 1, f_nodes + m * ((n-1)-1)]])    
    for j in range(1, m -1):
      tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1) + j -1,f_nodes + m * (n-1) + j + 1, f_nodes + m * ((n-1)-1) + j  ] ])  

    tile.append(["N{}".format(k) for k in [f_nodes + m * (n-1) + (m-1) -1, f_nodes + m * ((n-1)-1) + (m-1)  ] ])
   


    head_node = f_nodes + int(n/2)*m +  int((m)/2);



    return tile, head_node


def butterfly_gen(f_nodes,n):
    tile = []
    switches = []

    # add nodes ("Node"s)
    n_stages = log2(n)
    # first stage
    for i in range(0,n):
      tile.append(["S{}w{}w{}".format(f_nodes,0, int(i/2))])
    
    head_node = f_nodes + int(n/2)

    # add switches
    for k in range(1, n_stages):
      # each stage has (n/2) switches in our butterfly
      for i in range(0, int(n/2)):
        # current switch is (k-1, i)
        # it should be linked to two switches:
        #   both in the next layer k
        #   first one is to the direct next one,
        #   other one is to one bit flipped, the index of bit is k-1 from LEFT, hence (stages - k) from RIGHT
        switches.append(["S{}w{}w{}".format(f_nodes,k,i), "S{}w{}w{}".format(f_nodes,k,(i ^ (2**(n_stages - k - 1))))])

    # last stage (final layer of switches --> output nodes)
    for i in range(0, n/2): # note: n guaranteed to be divisble by 2
      switches.append(["N{}".format(f_nodes + n + i*2), "N{}".format(f_nodes + n + i*2 + 1)])
    
    # output nodes are connected to... nothing
    for i in range(0, n):
      tile.append([])

    return tile, head_node, switches

def folded_torus_gen(f_nodes,n,m):

    tile = []

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


def ring_head_gen(head_nodes,n,final_nodes):



    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [n - 1,1 ] ]) 

    for i in range(1,n-1) :
      final_nodes[head_nodes[i]].extend(["N{}".format(head_nodes[k]) for k in [i-1,i+1 ] ])  

    final_nodes[head_nodes[n-1]].extend(["N{}".format(head_nodes[k]) for k in [ n - 2,0] ])  



def chain_head_gen(head_nodes,n,final_nodes):


    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[1]) ])  

    for i in range(1, n-1) :
      final_nodes[head_nodes[i]].extend(["N{}".format(head_nodes[k]) for k in [i-1, i+1 ] ])  

    final_nodes[head_nodes[n-1]].extend(["N{}".format(head_nodes[n-2])])



def hypercube_head_gen(head_nodes,final_nodes):


    final_nodes[head_nodes[0]].extend(["N{}".format(head_nodes[k]) for k in [1,3,4 ]])  
    final_nodes[head_nodes[1]].extend(["N{}".format(head_nodes[k]) for k in [0,2,5 ]])  
    final_nodes[head_nodes[2]].extend(["N{}".format(head_nodes[k]) for k in [1,3,6 ]])  
    final_nodes[head_nodes[3]].extend(["N{}".format(head_nodes[k]) for k in [0,2,7 ]])  
    final_nodes[head_nodes[4]].extend(["N{}".format(head_nodes[k]) for k in [0,5,7 ]])  
    final_nodes[head_nodes[5]].extend(["N{}".format(head_nodes[k]) for k in [1,4,6 ]])  
    final_nodes[head_nodes[6]].extend(["N{}".format(head_nodes[k]) for k in [2,5,7 ]])  
    final_nodes[head_nodes[7]].extend(["N{}".format(head_nodes[k]) for k in [3,6,4 ]])  




def mesh_head_gen(head_nodes,n,m,final_nodes):


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
   



def butterfly_head_gen(head_nodes,n,final_nodes,final_switches):
    n_stages = log2(n)
    for i in range(0,n):
      # add the link to these new switches in the head nodes which will act as input
      final_nodes[head_nodes[i]].extend(["S{}w{}".format(0, int(i/2))])

    # add switches
    for k in range(1, n_stages):
      # each stage has (n/2) switches in our butterfly
      for i in range(0, int(n/2)):
        # current switch is (k-1, i)
        # it should be linked to two switches:
        #   both in the next layer k
        #   first one is to the direct next one,
        #   other one is to one bit flipped, the index of bit is k-1 from LEFT, hence (stages - k - 1) from RIGHT
        final_switches.append(["S{}w{}".format(k,i), "S{}w{}".format(k,(i ^ (2**(n_stages - k - 1))))])

    # last stage (final layer of switches --> output nodes)
    for i in range(0, n/2): # note: n guaranteed to be divisble by 2
      final_switches.append(["N{}".format(head_nodes[n + i*2]), "N{}".format(head_nodes[n + i*2 + 1])])
    
    
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






def print_func(final_nodes):
  file3 = open(r"Network.txt","w")

  for node_id in range(0,len(final_nodes)):
    print("NodeID: N{}".format(node_id),file=file3)
    print("Links : {}".format(len(final_nodes[node_id])),file=file3)

    for link in range(0,len(final_nodes[node_id])):
      print("L({}):{}".format(link,final_nodes[node_id][link]),file=file3)




file1 = open(r"L1Topology.txt","r")
file2 = open(r"L2Topology.txt","r")

L1 = file1.read()
L2 = file2.readlines()

L1_network_type = L1[0]
L1_n= int(L1[2])
L1_m = int(L1[4])


final_nodes = []
head_nodes = []
final_switches = []



#Adding the nodes and linking as per the tiles in L2 topology
for tile_i in L2:

  network_type = tile_i[0]
  n = int(tile_i[2])
  m = int(tile_i[4])
  f_nodes = len(final_nodes)

  if network_type == "R":
    tile, head_node = ring_gen(f_nodes,n)
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "C":
    tile, head_node = chain_gen(f_nodes,n)
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "M":
    tile, head_node = mesh_gen(f_nodes,n,m)
    final_nodes.extend(tile)
    head_nodes.append(head_node)

  elif network_type == "B":
    tile, head_node, switches = butterfly_gen(f_nodes,n,m)
    final_nodes.extend(tile)
    final_switches.extend(switches)
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



##Adding the head nodes links

if L1_network_type == "R":
    ring_head_gen(head_nodes,L1_n,final_nodes)
    
elif L1_network_type == "C":
    chain_head_gen(head_nodes,L1_n,final_nodes)
    
elif L1_network_type == "M":
    mesh_head_gen(head_nodes,L1_n,L1_m,final_nodes)
    
elif L1_network_type == "B":
    butterfly_head_gen(head_nodes,L1_n,final_nodes,final_switches)
    
elif L1_network_type == "F":
    folded_torus_head_gen(head_nodes,L1_n,L1_m,final_nodes)

elif L1_network_type == "H":
    hypercube_head_gen(head_nodes,final_nodes)
    
else :
    print("Invalid network type")


print_func(final_nodes)

