package butterfly_l2_node;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module butterfly_l2_node#(int k, Node_addr self_addr)(Ifc_node#(n_links));

  // Checks if the node is on the head side
  Bit#(1) head_side = (self_addr.L2_ID < 2**k)?1:0;
  
	/*
  For a straightforward algorithm, we assume there are 2 VCs on each node, one each for the two switches it is connected to on the output links 
  For a non-head node, there are only 2 input links from the different switches
  Hence, number of buffers required are 2*(2 + 1) - one for the core
  Hence there would be 4 VCs in total. VC1, VC2 correspond to link1, while VC3 and VC4 correspond to link2 
  Each input link would have buffers corresponding to these 4 VCs. Additionally, the flit generation module would have a buffer for 4 VCs (for uniformity, though a generated flit can only be inserted in the lower VC)
	*/


	// Instantiate the flit generation module
	Ifc_core core <- mkCore;

	// Instantiating VCs * (n_links + 1 ) number of FIFOs, which would act as the buffers.
	// The routers would store flits into the corresponding buffers, and the arbiter picks and transmits flits from its set of buffers in a round-robin fashion
	
	
  
  
	Vector#((n_links + 1)*4, FIFO#(Flit)) buff_vc <- replicateM(mkFIFO());
	
	// Registers to store the Round robin Count corresponding to each output link
	Reg#(int) round_robin_1 <- mkReg(1);
	Reg#(int) round_robin_2 <- mkReg(3);

	// Rule to get the flits from the Core
	
	rule get_core_flit;
	
		if core.gen_Flit                                 /// this rule to be handled
	
	endrule

	// Rules to update the Round Robin counter
	rule round_robin_count_1;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_1 == 1) round_robin_1 <= 2;
		else if (round_robin_1 == 2) round_robin_1 <= 5;
		else if (round_robin_1 == 5) round_robin_1 <= 6;
		else if (round_robin_1 == 6) round_robin_1 <= 9;
		else if (round_robin_1 == 9) round_robin_1 <= 10;
		else if (round_robin_1 == 10) round_robin_1 <= 1;
	endrule

	rule round_robin_count_2;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_2 == 3) round_robin_2 <= 4;
		else if (round_robin_2 == 4) round_robin_2 <= 7;
		else if (round_robin_2 == 7) round_robin_2 <= 8;
		else if (round_robin_1 == 8) round_robin_1 <= 11;
		else if (round_robin_1 == 11) round_robin_1 <= 12;
		else if (round_robin_2 == 12) round_robin_2 <= 3;
	endrule





	// Interface definitions

	channel[0] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_1 -1]);

			interface load_flit = interface Put#(Flit);   // check how to add int for VC (previous node should pass this) 
							method Action put(Flit f);
								if (f.fin_dest ! = self_addr)
									if (f.vc == 1)
									 	buff_vc[3].enqueue(f);
									else if (self_addr.row_num == 1)
										f.vc = 1;
										buff_vc[3].enqueue(f); 
									else
										buff_vc[2].enqueue(f);
								else
									core.consume_flit(f);
							endmethod
					     endinterface;

	channel[1] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_2 - 1]);

			interface load_flit = interface Put#(Flit);
							method Action put(Flit f);
								if (f.fin_dest ! = self_addr)
									if (f.vc == 1)
									 	buff_vc[1].enqueue(f);
									else if (self_addr.row_num == 2)
										f.vc = 1;
										buff_vc[1].enqueue(f);       
									else
										buff_vc[0].enqueue(f);
								else
									core.consume_flit(f);
							endmethod
					     endinterface;


endmodule

endpackage
