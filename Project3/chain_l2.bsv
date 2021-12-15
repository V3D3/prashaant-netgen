package chain_l2;

import Vector::*;
import toplevel_defs ::*;
import GetPut::*;
import FIFO::*;

module chain_l2#(int link_count, Node_addr self_addr, int len, int link_Pos, int link_Neg, Bool isHead, Bool isL1) (Ifc_node#(link_count));
    // Only one virtual channel per link, routing is simple shortest path
    // n_links: 1 (edge) / 2 (internal)
    // Core will have access to one input and one output buffer

    int linkPos = link_Pos;
    int linkNeg = link_Neg;
    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: headnode, 2: headnode and so on
    int nodelink_start = 1;
    if (isHead)
    begin
        nodelink_start = 2;
        linkPos = linkPos + 1;
        linkNeg = linkNeg + 1;
    end
    
    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL
    // int n_buffers = link_count * link_count;
    Vector#(32, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // the coords of head node in my topology
    int headIdx = len / 2;

    // my coord: my l2_ID

    Reg#(int) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a headrouter
    //      => I am either a non-head node (start: 1)
    //         or a head node (start: 2)

    Vector#(link_count,Ifc_channel) temp_node_channels;	
    
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
                            						// route it to an output buffer, if not mine
                            						if (f.fin_dest != self_addr)
                            						begin
                                						// assume destination is in different tile, route to head
                                						int destIdx = headIdx;
                                						if(self_addr.l1_headID == f.fin_dest.l1_headID)
                                    						// destination is in same tile
                                    						// route to dest
                                    							destIdx = f.fin_dest.l2_ID;
                                
						                                int diff = destIdx - self_addr.l2_ID;

                                						if(diff > 0)
                                    							buffers[link_count * i + linkPos].enq(f);
                                						else if(diff < 0)
                                    							buffers[link_count * i + linkNeg].enq(f);
                                						else
                                    							// it must go outwards, to L1 routing
                                    							if (isHead)
                                        							buffers[link_count * i + 1].enq(f);
                                    							else
                                        							// Error!
                                        							$display("error: chain_l2.bsv:86");
                            						end
                            						else
                                						// its mine, route it to the core
                                						buffers[link_count * i].enq(f);
                        					end
                    					endmethod
                					endinterface;
            			endinterface;
        end
    end
    else
    // Case: I am a head router (start: 1)
    begin
        for(int i = 0; i < link_count; i=i+1)
        begin
            // attach to input and output channels
            temp_node_channels[i] = interface Ifc_channel;
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit);
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
                            // route it to an output buffer, if not my tile's
                            int diff = f.fin_dest.l1_headID - self_addr.l1_headID;
                            if(diff > 0)
                                buffers[link_count * i + linkPos].enq(f);
                            else if(diff < 0)
                                buffers[link_count * i + linkNeg].enq(f);
                            else
                                // its my tile's, route it to my node, for L2 routing
                                buffers[link_count * i].enq(f);
                        end
                    endmethod
                endinterface;
            endinterface;
        end
    end

    interface node_channels = temp_node_channels;

endmodule: chain_l2
endpackage: chain_l2
