package common_defs;

import GetPut ::*;
import FIFO ::*;
import ClientServer ::*;


// Defining structure for Node address
typedef struct { 

	// Position of the tile in the L1 layer
	int Network_num;	
	// Node postion within the Tile
	int row_num;
	
	} Node_addr;  


// Defining a structure for the flit
typedef struct { 

	// Source address
	Node_addr src;
	// Final Destination address
	Node_addr fin_dest;
	// Local or current Destination address
	Node_addr cur_dest;	
	// Payload
	Bit#(`payload_size) payload;
	
	} Flit;



// Interface for the flit generator
interface Ifc_flit_gen;
	
	// method that returns a flit -- check who will set the enable for this
	method Flit flit_gen;

endinterface



// Module for generating flits at bottom level nodes
module mkFlitGen (Ifc_flit_gen);

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
	
	// Each channel is fully duplex, and each input link has a router and output link has an arbiter
	// Input channel - to be connected to router
	interface Get#(Flit) load_flit;
	// Output channel - sends flits from the arbiter
	interface Put#(Flit) send_flit; 
endinterface

endpackage

