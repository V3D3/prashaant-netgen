package butterfly_l2_node;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module butterfly_l2_node#(int k, Ifc_core core, Node_addr self_addr)(Ifc_node#(n_links));

  // Checks if the node is on the head side
  Bit#(1) head_side = (self_addr.L2_ID < 2**k)?1:0;
  
  // am I a head node?
  Bool isHead = $$1;
  
  // the coords of head node in my topology
  int headIdx = 0;
  
  // Treat core as a channel (IL / OL)
  // A non head butterfly node will have only a single channel that connects it to a switch. Including 1 buffer for the core, we require 2 buffers
  

  // The routers would store flits into the corresponding buffers, and the arbiter picks and transmits flits from its set of buffers in a round-robin fashion
	
	// Buffers for the L2 routing/ channels
	Vector#((n_links + 1)*(n_links + 1), FIFO#(Flit)) buff_vc <- replicateM(mkFIFO());     // buff_vc[0] is for the input link, and buff_vc[1] is for the core
	$$0
	
	
	
	// Register to store the Round robin Count for the single internal output link
	Reg#(int) round_robin <- mkReg(0);

	// Rule to get the flits from the Core
	
	rule get_core_flit;
	
		if core.gen_Flit                                 /// this rule to be handled
	
	endrule

	// Rules to update the Round Robin counter
	rule round_robin_count;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_1 == 1) round_robin <= 0;
		else 			round_robin <= 1;

	endrule






	// Interface definitions

	channel[0] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_1]);

	// A flit that comes in to a node in butterfly has to be consumed unless it is a head node
	
			interface load_flit = interface Put#(Flit);   // check how to add int for VC (previous node should pass this) 
							method Action put(Flit f);
								if (f.fin_dest ! = self_addr)
									$display("Illegal routing. This node cannot be accessed");
									core.
								else
								
							endmethod
					     endinterface;



endmodule

endpackage
