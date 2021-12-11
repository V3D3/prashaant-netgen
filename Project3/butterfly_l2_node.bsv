package butterfly_l2_node;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module butterfly_l2_node#(int k, Ifc_core core, Node_addr self_addr, Bool isL1)(Ifc_node#(n_links));

    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: other headnode, 2: other headnode and so on
    int link_count = n_links + 1;

    if (isHead)
        link_count = link_count + 1;

    int nodelink_start = 1;
    
    if (isHead)
    begin
        nodelink_start = 2;
    end
    
    
    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL
    Vector#(link_count * link_count, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // the coords of head node in my topology
    int headIdx = 0;

    // my coord: my L2_ID

    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)                      
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a L1 headrouter
    //      => I am either a non-head node (start: 1)
    //         or a head node (start: 2)
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
                            // route it to an output buffer, if not mine
                            if (f.fin_dest != self_addr)
                            begin
                                // assume destination is in different tile, route to head
                                int destIdx = 0;
                                if(self_addr.l1_headID == f.fin_dest.l1_headID)
					destIdx = f.fin_dest.l2_ID;
				if((destIdx < 2**k && self_addr.l2_ID < 2**k) || (destIdx > 2**k && self_addr.l2_ID > 2**k))
					// Error
					$display("Illegal routing in butterfly");
				else if (destIdx != self_addr.l2_ID)
				begin
                                    // destination is in same tile
                                    // route to dest
                                    destIdx = f.fin_dest.l2_ID;
				    
       	                            buffers[link_count * i].enq(f);
         			 end
				    

				 else
                                    // it must go outwards, to L1 routing
                                    if (isHead)
                                        buffers[link_count * i + 1].enq(f);
                                    else
                                        // Error!
					$display("Error");
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
			    if(f.fin_dest.l1_headID == self_addr.l1_headID)
                                // its mine, route it to the node for internal routing
                                buffers[2*link_count * i].enq(f);

			    else if((f.fin_dest.l1_headID < 2**k && self_addr.l1_headID < 2**k) || (f.fin_dest.l1_headID > 2**k && self_addr.l1_headID > 2**k))
				// Error
				$display("Illegal routing in butterfly");
                            else
       	                        buffers[link_count * i].enq(f);				    
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end




endmodule

endpackage
