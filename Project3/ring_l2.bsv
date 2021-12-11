package ring_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module ring_l2#(int n_links, Ifc_core core, Node_addr self_addr)(Ifc_node#(n_links));

	/*
	 Date line algorithm is to be implemented.
	 A L2 ring node will have 2 VCs per output link, and n_links would be 2 by default
	 Hence there would be 4 VCs in total. VC1, VC2 correspond to link1, while VC3 and VC4 correspond to link2 
	 Each input link would have buffers corresponding to these 4 VCs. Additionally, the flit generation module would have a buffer for 4 VCs (for uniformity, though a generated flit can only be inserted in the lower VC)
	*/

    int link_count = n_links + 1;
    int linkPos = link_count;
    int linkNeg = 0;

    if (isHead)
        link_count = link_count + 1;

    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: other headnode, 2: other headnode and so on
    int nodelink_start = 1;
    
    if (isHead)
    begin
        nodelink_start = 2;
        linkPos = linkPos + 1;
        linkNeg = linkNeg + 1;
    end
    
    
    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL*2 (2 VCs for ring)
    Vector#(link_count * link_count*2, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // the coords of head node in my topology
    int headIdx = 0;

    // my coord: my L2_ID

    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count*2 - 1)                      // *2 indicates VCs
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
                                int destIdx = headIdx;
                                if(self_addr.l1_headID == f.fin_dest.l1_headID)
					// destination is in the same tile
					destIdx = f.fin_dest.l2_ID
				if(self_addr.l2_ID != destIdx)
				begin
                                    // destination is in same tile
                                    // route to dest
                                    destIdx = f.fin_dest.l2_ID;
				    
	                            if(f.vc = 1)
        	                            buffers[2*link_count * i + linkPos + ((i==1)?2:1)].enq(f);
                	            else
				    begin
				    	if(self_addr.l2_ID == 1)
					begin
					    f.vc  = 1;
                        	            buffers[2*link_count * i + linkPos + ((i==1)?2:1)].enq(f);
					end
					else 
                        	            buffers[2*link_count * i + linkNeg + ((i==1)?2:1)].enq(f);
				    end
				 end   

				 else
                                    // it must go outwards, to L1 routing
                                    if (isHead)
                                        buffers[2*link_count * i + 1].enq(f);
                                    else
                                        // Error!
					$display("Error");
                            end
                            else
                                // its mine, route it to the core
                                buffers[2*link_count * i].enq(f);
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
			    begin
	                            if(f.vc = 1)
        	                            buffers[2*link_count * i + linkPos + ((i==1)?2:1)].enq(f);
                	            else
				    begin
				    	if(self_addr.l1_headID == 1)
					begin
					    f.vc  = 1;
                        	            buffers[2*link_count * i + linkPos + ((i==1)?2:1)].enq(f);
					end
					else 
                        	            buffers[2*link_count * i + linkPos + ((i==1)?2:1)].enq(f);
				    end
				    
		            end
                            else
                                // its mine, route it to the node for internal routing
                                buffers[2*link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end

endmodule

endpackage


