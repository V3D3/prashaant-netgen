package ring_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module ring_l2#(int n_links, Node_addr self_addr)(Ifc_node#(n_links));

	/*
	 Date line algorithm is to be implemented.
	 A L2 ring node will have 2 VCs per output link, and n_links would be 2 by default
	 Hence there would be 4 VCs in total. VC1, VC2 correspond to link1, while VC3 and VC4 correspond to link2 
	 Each input link would have buffers corresponding to these 4 VCs. Additionally, the flit generation module would have a buffer for 2 VCs, since a generated flit can only be inserted in the lower VC
	*/


	// Instantiate the flit generation module
	Ifc_flit_gen generator <- mkFlitGen;

	// Instantiating VCs * n_links number of FIFOs, which would act as the buffers.
	// The routers would store flits into the corresponding buffers, and the arbiter picks and transmits flits from its set of buffers in a round-robin fashion
	

	Vector#((n_links + 1)*4, FIFO#(Flit)) buff_vc <- replicateM(mkFIFO());
	
	// Registers to store the Round robin Count corresponding to each output link
	Reg#(int) round_robin_1 <- mkReg(1);
	Reg#(int) round_robin_2 <- mkReg(3);


	// Rules to update the Round Robin counter
	rule round_robin_count_1;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_1 == 1) round_robin_1 <= 2;
		else if (round_robin_1 == 2) round_robin_1 <= 5;
		else if (round_robin_1 == 5) round_robin_1 <= 6;
		else if (round_robin_1 == 6) round_robin_1 <= 1;
	endrule

	rule round_robin_count_2;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_2 == 3) round_robin_2 <= 4;
		else if (round_robin_2 == 4) round_robin_2 <= 7;
		else if (round_robin_2 == 7) round_robin_2 <= 8;
		else if (round_robin_2 == 8) round_robin_2 <= 3;
	endrule





	// Interface definitions

	channel[0] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_1 -1]);

			interface load_flit = interface Put#(Flit);
							method Action put(Flit f);
								if (f.fin_dest ! = self_addr)
									if (f.vc == 1)
									 	buff_vc[3].enqueue(f);
									else if (self_addr.row_num == 1)
										buff_vc[3].enqueue(f);       ////// ********** UPDATE ITS VC also !!!!!!
									else
										buff_vc[2].enqueue(f);
								else
									generator.consume_flit(f);
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
										buff_vc[1].enqueue(f);       ////// ********** UPDATE ITS VC also !!!!!!
									else
										buff_vc[0].enqueue(f);
								else
									generator.consume_flit(f);
							endmethod
					     endinterface;


endmodule

endpackage



/*************************************************************************************************************************
*********************** ADDITIONAL CODE -- IGNORE ************************************************************************
***************************************************************************************************************************


	// FIFOs for VC1 - an additional FIFO is for the flits generated that are inserted in vc_1 
//	Vector#(n_links + 1, FIFO#(Flit)) buff_vc1 <- replicateM(mkFIFO());

	// FIFOs for VC2
//	Vector#(n_links, FIFO#(Flit)) buff_vc2 <- replicateM(mkFIFO());

	// FIFOs for VC3 - an additional FIFO is for the flits generated that are inserted in vc_1 
//	Vector#(n_links + 1, FIFO#(Flit)) buff_vc3 <- replicateM(mkFIFO());

	// FIFOs for VC4
//	Vector#(n_links, FIFO#(Flit)) buff_vc4 <- replicateM(mkFIFO());


	for (i=0; i < n_links; i = i+1) begin
		channels[i] = interface Ifc_channel;
					if (round_robin % 2 == 1)
						interface send_flit = toPut(buff_vc2[round_robin/2]);
					else
						interface send_flit = toPut(buff_vc1[round_robin/2]);

					interface load_flit = toGet(
	
			      endinterface;
	end

*************************************************************************************************************************
*********************** ADDITIONAL CODE -- IGNORE ************************************************************************
***************************************************************************************************************************/
