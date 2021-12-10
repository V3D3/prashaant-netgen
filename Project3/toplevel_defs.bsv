package common_defs;

import GetPut ::*;
import FIFO ::*;
import ClientServer ::*;


// Defining structure for Node address
typedef struct { 

	// Position of the tile in the L1 layer
	int L1_headID;	
	// Node postion within the Tile
	int L2_ID;
	
	} Node_addr;  


// Defining a structure for the flit
typedef struct { 

	// Source address
	Node_addr src;
	// Final Destination address
	Node_addr fin_dest;
	// Payload
	Bit#(`payload_size) payload;
	
	} Flit;



// Interface for the flit generator
interface Ifc_core;
	
	// method that returns a flit -- check who will set the enable for this
	method Flit gen_flit;
	method Action consume_flit(Flit f);

endinterface


This part is to be done by the end user - simulator in our case
// Module for generating and core flits at bottom level nodes
module mkCore #(num_(Ifc_core);

	// LFSR for random patterns 
	LFSR#( Bit#(8) ) lfsr <- mkLFSR_8 rand ;	

	
	<<<< insert flit generation code >>>>>

endmodule



// Interfaces for the nodes
interface Ifc_node#(n_links);   // Since the links are fully duplex, number of input links and output links would be the same

	// The interface for the nodes are basically the set of duplex channels connecting it to other nodes. 
	// n_links is the parametrised number of channels that the node contains.
	// Defining a n_link dimensional Vector of channel interfaces.
	interface Vector#(n_links,Ifc_channel) node_channels;	

	// Note : Each of these channels are individually accessible and connectable from the top module

endinterface

interface Ifc_channel;
	
	interface Put#(Flit) load_flit;
	interface input_link il;
	// Output channel - sends flits from the arbiter
	interface Get#(Flit) send_flit; 
	
endpackage

