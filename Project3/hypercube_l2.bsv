package hypercube_l2;

import Vector::*;
import toplevel_defs ::*;
import GetPut::*;
import FIFO::*;

module hypercube_l2#(int link_count, Node_addr self_addr, int link_Diff2, int link_Diff1, int link_Diff0, Bool isHead, Bool isL1) (Ifc_node#(link_count));
    // Eight virtual channels per link, routing is via flipping Most Significant Differing Bit
    // n_links: 3 (all)
    // Core will have access to one input and one output buffer

    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: headnode, 2: headnode and so on
    int nodelink_start = 1;
    int linkDiff2 = link_Diff2;
    int linkDiff1 = link_Diff1;
    int linkDiff0 = link_Diff0;
    if (isHead)
    begin
        nodelink_start = 2;
        linkDiff2 = linkDiff2 + 1;
        linkDiff1 = linkDiff1 + 1;
        linkDiff0 = linkDiff0 + 1;
    end

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL  VCs
//    int n_buffers = link_count * link_count * 8;
    Vector#(200, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    // up to n_links - 1: ILi
    
    // we have link_count buckets of size link_count * 8
    // one bucket per IL
    // each bucket has 8 sections, each of size link_count
    // one section per VC
    // each section has link_count FIFOs
    // one FIFO per OL

    // the coords of head node in my topology
    int headIdx = 0;

    // round robin and its incrementer, for arbiter
    Reg#(int) arbiter_rr_counter <- mkReg(0);
    Reg#(int) arbiter_rr_vc_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
        begin
            arbiter_rr_counter <= 0;
            if (arbiter_rr_vc_counter < 7)
                arbiter_rr_vc_counter <= arbiter_rr_vc_counter + 1;
            else
                arbiter_rr_vc_counter <= 0;
        end
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
                interface send_flit = toGet(buffers[8 * link_count * arbiter_rr_counter
                                                +   link_count * arbiter_rr_vc_counter
                                                +   i]);
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
                                
                                int diff = destIdx ^ self_addr.l2_ID;
                                int offset = 8 * link_count * i + destIdx * link_count;

                                if (diff != 0)
                                    f.vc = destIdx;

                                if(diff >= 4)
                                    buffers[linkDiff2 + offset].enq(f);
                                else if(diff >= 2)
                                    buffers[linkDiff1 + offset].enq(f);
                                else if(diff >= 1)
                                    buffers[linkDiff0 + offset].enq(f);
                                else
                                    if (isHead)
                                        buffers[8 * link_count * i + 1].enq(f);
                                    else
                                        // Error!
                                        $display("error: hypercube_l2.bsv:110");
                            end
                            else
                                // its mine, route it to the core
                                buffers[8 * link_count * i].enq(f);
                        end
                    endmethod
                endinterface;
            endinterface; // Ifc_channel
        end
    end
    else
    // Case: I am a head router (L1)
    begin
        for(int i = 0; i < link_count; i=i+1)
        begin
            // attach to input and output channels
            temp_node_channels[i] = interface Ifc_channel
                // send flit from me to others
                interface send_flit = toGet(buffers[8 * link_count * arbiter_rr_counter
                                                +   link_count * arbiter_rr_vc_counter
                                                +   i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit)
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
                            int destIdx = f.fin_dest.l1_headID;
                                
                            int diff = destIdx ^ self_addr.l1_headID;
                            int offset = 8 * link_count * i + destIdx * link_count;

                            if (diff != 0)
                                f.vc = destIdx;

                            if(diff >= 4)
                                buffers[linkDiff2 + offset].enq(f);
                            else if(diff >= 2)
                                buffers[linkDiff1 + offset].enq(f);
                            else if(diff >= 1)
                                buffers[linkDiff0 + offset].enq(f);
                            else
                                // its my tile's, route it to my node for L2 routing
                                buffers[8 * link_count * i].enq(f);
                        end
                    endmethod
                endinterface;
            endinterface; // Ifc_channel
        end
    end

    interface node_channels = temp_node_channels;

endmodule: hypercube_l2
endpackage: hypercube_l2
