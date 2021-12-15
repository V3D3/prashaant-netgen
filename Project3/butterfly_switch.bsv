package butterfly_switch;

import Vector::*;
import toplevel_defs ::*;
import GetPut::*;
import FIFO::*;


module butterfly_switch#(int k, Butterfly_switch_addr self_addr, Bool isL1)(Ifc_node#(4));

        // In case of a L2 butterfly topology, Channel 0,1 are towards the head, and 2,3 are away from head
	// Links 0 and 2 are direct links, while 1 and 3 are diagonal links
  
    // A butterfly switch has 4 links by default
    int link_count = 4;
    
    int prev_diag_switch = (1 << (self_addr.stage - 2)) ^ self_addr.pos;
    int next_diag_switch = (1 << (self_addr.stage - 1)) ^ self_addr.pos;
    
    
    // buffers for:
    //       each IL    for each OL
//    int n_buffers = link_count * link_count;
    Vector#(32, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // my coord: my L2_ID

    Reg#(int) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)                      
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a L1 switch

    Vector#(4, Ifc_channel) temp_node_channels;	

    if (!isL1)
    begin
        for(int i = 0; i < link_count; i=i+1)
        begin
            // attach to input and output channels
            temp_node_channels[i] = interface Ifc_channel
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit)
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
			    // assume destination is head
		       	    int destIdx = 0;
                            if (f.fin_dest.l1_headID == self_addr.l1_headID)
			    	destIdx = f.fin_dest.l2_ID;
			    if (destIdx < 2**(k-1))
                            begin
                                // route to the head side
				if (self_addr.stage != 1)
					if ((destIdx & (1 << (self_addr.stage - 1))) != (self_addr.pos & (1 << (self_addr.stage - 2))))
					// Go diagonally
					buffers[link_count * i + 1].enq(f);
					
					else
					// Go straight
					buffers[link_count * i + 0].enq(f);					
				else
					if ((destIdx & (1 << (self_addr.stage - 1))) != 0)
					// Go diagonally
					buffers[link_count * i + 1].enq(f);					
					else
					// Go straight
					buffers[link_count * i + 0].enq(f);
					
			    end
			    
			    else
			    begin
			    	// route away from the head
				if ((destIdx & (1 << (self_addr.stage - 1))) != (self_addr.pos & (1 << (self_addr.stage - 1))))
				// Go diagonally
					buffers[link_count * i + 3].enq(f);					
				else
				// Go straight
					buffers[link_count * i + 2].enq(f);					
			    end						
				
                        end
                    endmethod
                endinterface;
            endinterface; //  Ifc_channel
        end
    end
    else
    // Case: I am in a L1 topology (start: 1)
    begin
        for(int i = 0; i < link_count; i=i+1)
        begin
            // attach to input and output channels
            temp_node_channels[i] = interface Ifc_channel
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit)
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
		       	    int destIdx = f.fin_dest.l1_headID; 
                            if (destIdx < 2**(k-1)) 
                            begin
                                // Route towards head
				if (self_addr.stage != 1)
					if ((destIdx & (1 << (self_addr.stage - 1))) != (self_addr.pos & (1 << (self_addr.stage - 2))))
					// Go diagonally
					buffers[link_count * i + 1].enq(f);
					
					else
					// Go straight
					buffers[link_count * i + 0].enq(f);					

				else
					if ((destIdx & (1 << (self_addr.stage - 1))) != 0)
					// Go diagonally
					buffers[link_count * i + 1].enq(f);					
					
					else
					// Go straight
					buffers[link_count * i + 0].enq(f);

			    end
			    
			    else
			    begin
			    	// Route away from head
				if ((destIdx & (1 << (self_addr.stage - 1))) != (self_addr.pos & (1 << (self_addr.stage - 1))))
					// Go diagonally
					buffers[link_count * i + 3].enq(f);					
					
				else
					// Go straight
					buffers[link_count * i + 2].enq(f);					

			    end						
				
                        end
                    endmethod
                endinterface;
            endinterface; // Ifc_channel
        end
    end

    interface node_channels = temp_node_channels;

endmodule

endpackage
