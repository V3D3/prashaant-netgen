/******************************************************
********** UNDER DEV -- MAJOR CHANGES REQD. ***********
******************************************************/

package ring_l1;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

///*************** VCs are corresponding algo for head node to be determined using L1 network!!!!!!

module ring_l1#(int n_links, Node_addr self_addr)(Ifc_node#(n_links));

	/*
	 Date line algorithm is to be implemented.
	 A L1 ring node will have 2 VCs per output link, and n_links would be 3 by default
	 Hence there would be 6 VCs in total. VC1, VC2 correspond to link1, while VC3 and VC4 correspond to link2, VC5 and VC6 correspond to link3 
	 Each input link would have buffers corresponding to these 6 VCs. Additionally, the flit generation module would have a buffer for 2 VCs, since a generated flit can only be inserted in the lower VC
	*/


	// Instantiate the flit generation module  --- ************ Specs say L1 doesn't have generator.. hmm?
	Ifc_flit_gen generator <- mkFlitGen;

	// Instantiating VCs * n_links number of FIFOs, which would act as the buffers.
	// The routers would store flits into the corresponding buffers, and the arbiter picks and transmits flits from its set of buffers in a round-robin fashion
	

	Vector#((n_links + 1)*6, FIFO#(Flit)) buff_vc <- replicateM(mkFIFO());
	
	// Registers to store the Round robin Count corresponding to each output link
	Reg#(int) round_robin_1 <- mkReg(1);
	Reg#(int) round_robin_2 <- mkReg(3);
	Reg#(int) round_robin_2 <- mkReg(5);

	// Rules to update the Round Robin counter
	rule round_robin_count_1;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_1 == 1) round_robin_1 <= 2;
		else if (round_robin_1 == 2) round_robin_1 <= 7;
		else if (round_robin_1 == 7) round_robin_1 <= 8;
		else if (round_robin_1 == 8) round_robin_1 <= 13;
		else if (round_robin_1 == 13) round_robin_1 <= 14;
		else if (round_robin_1 == 14) round_robin_1 <= 1;
	endrule

	rule round_robin_count_2;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_2 == 3) round_robin_2 <= 4;
		else if (round_robin_2 == 4) round_robin_2 <= 9;
		else if (round_robin_2 == 9) round_robin_2 <= 10;
		else if (round_robin_2 == 10) round_robin_2 <= 15;
		else if (round_robin_2 == 15) round_robin_2 <= 16;
		else if (round_robin_2 == 16) round_robin_2 <= 3;
	endrule

	rule round_robin_count_3;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_3 == 5) round_robin_3 <= 6;
		else if (round_robin_3 == 6) round_robin_3 <= 11;
		else if (round_robin_3 == 11) round_robin_3 <= 12;
		else if (round_robin_3 == 12) round_robin_3 <= 17;
		else if (round_robin_3 == 17) round_robin_3 <= 18;
		else if (round_robin_3 == 18) round_robin_3 <= 5;
	endrule




	// Interface definitions

	channel[0] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_1 -1]);

			interface load_flit = interface Put#(Flit);
							method Action put(Flit f);
								if (f.fin_dest == self_addr)
									generator.consume_flit(f);
								else if (f.cur_dest==f.fin_dest)     // Route inwards
									if (f.vc == 1)
									 	buff_vc[3].enqueue(f);
									else if (self_addr.row_num == 1)
										buff_vc[3].enqueue(f);       ////// ********** UPDATE ITS VC also !!!!!!
									else
										buff_vc[2].enqueue(f);
								else				     // Route outwards
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
