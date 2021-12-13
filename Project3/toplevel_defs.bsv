package toplevel_defs;

import GetPut ::*;
import FIFO ::*;
import ClientServer ::*;
import Vector ::*;
import Connectable ::*;

// Defining structure for Node address
typedef struct { 

	// Position of the tile in the L1 layer
	int l1_headID;	
	// Node postion within the Tile
	int l2_ID;
	
	} Node_addr;  

// Defining structure for Butterfly Switch address
typedef struct { 

	// Position of the tile in the L1 layer
	int l1_headID;
	// Stage in the topology
	int stage;
	// Switch position in stage
	int pos;
	
	} Butterfly_switch_addr;  


// Defining a structure for the flit
typedef struct { 

	// Is this flit valid?
	Bit#(1) valid;
	// Source address
	Node_addr src;
	// Final Destination address
	Node_addr fin_dest;
	// Payload
	Bit#(32) payload;
	
	int vc;
	
	} Flit;



// Interface for the Core - flit generator + consumer
interface Ifc_core;
	
	interface Get#(Flit) send_flit;
	interface Put#(Flit) load_flit;

endinterface


// This part is to be done by the end user - simulator in our case
// Module for generating and core flits at bottom level nodes
/*
module mkCore (Ifc_core);


endmodule
*/


// Interfaces for the nodes
interface Ifc_node#(type n_links);   // Since the links are fully duplex, number of input links and output links would be the same

	// The interface for the nodes are basically the set of duplex channels connecting it to other nodes. 
	// n_links is the parametrised number of channels that the node contains.
	// Defining a n_link dimensional Vector of channel interfaces.
	interface Vector#(n_links,Ifc_channel) node_channels;	

	// Note : Each of these channels are individually accessible and connectable from the top module

endinterface

interface Ifc_channel;

	// Input channel - loads filt from the previous node for routing
	interface Put#(Flit) load_flit;
	// Output channel - sends flits from the arbiter
	interface Get#(Flit) send_flit; 

endinterface	


instance Connectable #(Ifc_channel,
		       Ifc_channel);

   module mkConnection #(Ifc_channel channel_a,
			 Ifc_channel channel_b )
		       (Empty);
		       
		       mkConnection (channel_a.send_flit, channel_b.load_flit);
		       mkConnection (channel_b.send_flit, channel_a.load_flit);
		       
   endmodule: mkConnection
endinstance: Connectable

endpackage
