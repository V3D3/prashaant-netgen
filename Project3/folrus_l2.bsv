package folrus_l2;

import Vector::*;
import toplevel_defs ::*;
import GetPut::*;
import FIFO::*;

module folrus_l2#(int link_count, Node_addr self_addr, int rows, int cols, int link_XPos, int link_XNeg, int link_YPos, int link_YNeg, Bool isHead, Bool isL1) (Ifc_node#(link_count));
    // Two virtual channels per link, routing is X (for locating ring, shortest arc), then Date-line in Y
    // n_links: 4 (all)
    // Core will have access to one input and one output buffer

    int linkXPos = link_XPos;
    int linkXNeg = link_XNeg;
    int linkYPos = link_YPos;
    int linkYNeg = link_YNeg;

    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: headnode, 2: headnode and so on
    int nodelink_start = 1;
    if (isHead)
    begin
        nodelink_start = 2;
        linkXPos = linkXPos + 1;
        linkXNeg = linkXNeg + 1;
        linkYPos = linkYPos + 1;
        linkYNeg = linkYNeg + 1;
    end

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL  VCs
//    int n_buffers = link_count * link_count * 2; 
    Vector#(32, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    
    // we have link_count buckets of size link_count * 2
    // one bucket per IL
    // each bucket has 2 sections, each of size link_count
    // one section per VC
    // each section has link_count FIFOs
    // one FIFO per OL

    // the coords of head node in my topology
    int headIdx = 0;
    
    // my coords in the FT
    int myRow;
    int myCol;
    if (!isL1)
    begin
        myRow = self_addr.l2_ID / rows;
        myCol = self_addr.l2_ID % rows;
    end
    else
    begin
        myRow = self_addr.l1_headID / rows;
        myCol = self_addr.l1_headID % rows;
    end

    // round robin and its incrementer, for arbiter
    Reg#(int)  arbiter_rr_counter <- mkReg(0);
    Reg#(int)       arbiter_rr_vc_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
        begin
            arbiter_rr_counter <= 0;
            arbiter_rr_vc_counter <= ~arbiter_rr_vc_counter;
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
                interface send_flit = toGet(buffers[2 * link_count * arbiter_rr_counter
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
                                // destination is in different tile (default), route to head
                                int destIdx = headIdx;
                                if(self_addr.l1_headID == f.fin_dest.l1_headID)
                                    // destination is in same tile
                                    // route to dest
                                    destIdx = f.fin_dest.l2_ID;
                                
                                int diffRow = (destIdx / rows) - myRow;
                                int diffCol = (destIdx % rows) - myCol;
                                
                                if (diffCol != 0)
                                    if(diffCol > 0)
                                        buffers[2 * link_count * i + linkXPos].enq(f);
                                    else
                                        buffers[2 * link_count * i + linkXNeg].enq(f);
                                else if(diffRow != 0)
                                begin
                                    int idx = 2 * link_count * i;
                                    if(diffRow > 0)
                                        idx = idx + linkYPos;
                                    else
                                        idx = idx + linkYNeg;

                                    if ((f.vc == 1) || (myRow == 1))
                                    begin
                                        idx = idx + link_count;
                                        f.vc = 1;
                                    end
                                    
                                    buffers[idx].enq(f);
                                end
                                else
                                    if (isHead)
                                        buffers[2 * link_count * i + 1].enq(f);
                                    else
                                        // Error!
                                        $display("error: folrus_l2.bsv:131");
                            end
                            else
                                // its mine, route it to the core
                                buffers[2 * link_count * i].enq(f);
                        end
                    endmethod
                endinterface;
            endinterface; // Ifc_channel
        end
    end
    else
    begin
        for(int i = 0; i < link_count; i = i+1)
        begin
            // attach to input and output channels
            temp_node_channels[i] = interface Ifc_channel
                // send flit from me to others
                interface send_flit = toGet(buffers[2 * link_count * arbiter_rr_counter
                                                +   link_count * arbiter_rr_vc_counter
                                                +   i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit)
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
                            int destIdx = f.fin_dest.l1_headID;

                            int diffRow = (destIdx / rows) - myRow;
                            int diffCol = (destIdx % rows) - myCol;

                            if (diffCol != 0)
                                if (diffCol > 0)
                                    buffers[2 * link_count * i + linkXPos].enq(f);
                                else
                                    buffers[2 * link_count * i + linkXNeg].enq(f);
                            else if(diffRow != 0)
                            begin
                                int idx = 2 * link_count * i;
                                if(diffRow > 0)
                                    idx = idx + linkYPos;
                                else
                                    idx = idx + linkYNeg;

                                if ((f.vc == 1) || (myRow == 1))
                                begin
                                    idx = idx + link_count;
                                    f.vc = 1;
                                end
                                
                                buffers[idx].enq(f);
                            end
                            else
                                buffers[2 * link_count * i].enq(f);
                            
                        end
                    endmethod
                endinterface;
            endinterface; // Ifc_channel
        end
    end

    interface node_channels = temp_node_channels;

endmodule: folrus_l2
endpackage: folrus_l2
