package butterfly_switch;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module butterfly_switch#(int k, Bool isL1, Butterfly_switch_addr self_addr)(Ifc_node#(n_links));

        // In case of a L2 butterfly topology, Channel 0,1 are towards the head, and 2,3 are away from head
	// Links 0 and 2 are direct links, while 1 and 3 are diagonal links
  
    // A butterfly switch has 4 links by default
    int link_count = 4;
    
    
    // buffers for:
    //       each IL    for each OL
    Vector#(link_count * link_count, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // my coord: my L2_ID

    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)                      
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a L1 switch
    if (!isL1)
    begin
        for(int i = 0; i < link_count; i++)
        begin
            // attach to input and output channels
            node_channels[i] = interface Ifc_channel;
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit);
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
		       	    int destIdx = 0; 
                            // route it to an output buffer, if not mine
                            if (f.fin_dest.l1_headID != self_addr.l1_headID)
                            begin
                                // destination is in different tile, route to head
				

			    if(self_addr.l1_headID == f.fin_dest.l1_headID)
				begin
                                    // destination is in same tile
                                    // route to dest
				    
       	                            buffers[link_count * i].enq(f);
         			 end
				    

				 else
                                    // it must go outwards, to L1 routing
                                    if (isHead)
                                        buffers[link_count * i + 1].enq(f);
                                    else
                                        // Error!
                            end
                            else
                                // its mine, route it to the core
                                buffers[link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end
    else
    // Case: I am a L1 head router (start: 1)
    begin
        for(int i = 0; i < link_count; i++)
        begin
            // attach to input and output channels
            node_channels[i] = interface Ifc_channel;
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit);
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
			    if(f.fin_dest.l1_headID != self_addr.l1_headID)
       	                            buffers[link_count * i].enq(f);				    
                            else
                                // its mine, route it to the node for internal routing
                                buffers[2*link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end
//
endmodule

endpackage
