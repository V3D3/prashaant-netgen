package folrus_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module folrus_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int rows, int cols, int linkXPos, int linkXNeg, int linkYPos, int linkYNeg) (Ifc_node#(n_links));
    // Two virtual channels per link, routing is X (for locating ring, shortest arc), then Date-line in Y
    // n_links: 4 (all)
    // Core will have access to one input and one output buffer

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //         each IL       for each OL   VCs
    Vector#((n_links + 1) * (n_links + 1) * 2, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0
    // we have (n_links + 1) buckets of size (n_links + 1) * 2
    // one bucket per IL
    // each bucket has 2 sections, each of size (n_links + 1)
    // one section per VC
    // each section has n_links + 1 FIFOs
    // one FIFO per OL

    // the coords of head node in my topology
    int headIdx = 0;

    // my coords in the FT
    int myRow = self_addr.L2_ID / rows;
    int myCol = self_addr.L2_ID % rows;

    // am i a head node?
    bool isHead = $$1;

    // round robin and its incrementer, for arbiter
    Reg#(UInt#(3))  arbiter_rr_counter <- mkReg(0);
    Reg#(Bit)       arbiter_rr_vc_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < n_links)
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
        begin
            arbiter_rr_counter <= 0;
            arbiter_rr_vc_counter <= ~arbiter_rr_vc_counter;
        end
    endrule

    $$2

    ////////// Link Rules
    // for each of my links
    for(int i = 0; i <= n_links; i++)
    begin
        // attach to input and output channels
        node_channels[i] = interface Ifc_channel;
            // send flit from me to others
            interface send_flit = toGet(buffers[2 * n_links * arbiter_rr_counter
                                            +   n_links * arbiter_rr_vc_counter
                                            +   i]);
            // receive a flit from somewhere
            interface load_flit = interface Put#(Flit);
                method Action put(Flit f);
                    if(f.valid == 1)
                    begin
                        // route it to an output buffer, if not mine
                        if (f.fin_dest != self_addr)
                        begin
                            int destIdx = 0;
                            if(self_addr.L1_headID == f.fin_dest.L1_headID)
                                // destination is in same tile
                                // route to dest
                                destIdx = f.fin_dest.L2_ID;
                            else
                                // destination is in different tile
                                // route to my tile's head
                                destIdx = headIdx;
                            
                            int diffRow = (destIdx / rows) - myRow;
                            int diffCol = (destIdx % rows) - myCol;
                            
                            if (diffCol != 0)
                                if(diffCol > 0)
                                    buffers[2 * n_links * i + linkXPos].enq(f);
                                else
                                    buffers[2 * n_links * i + linkXNeg].enq(f);
                            else if(diffRow != 0)
                            begin
                                int idx = 2 * n_links * i;
                                if(diffRow > 0)
                                    idx += linkYPos;
                                else
                                    idx += linkYNeg;

                                if ((f.vc == 1) || (myRow == 1))
                                begin
                                    idx = idx + n_links;
                                    f.vc = 1;
                                end
                                
                                buffers[idx].enq(f);
                            end
                            $$3
                        end
                        else
                            // its mine, route it to the core
                            buffers[2 * n_links * i].enq(f);
                    end
                endmethod
            endinterface
        endinterface: Ifc_channel
    end

endmodule: folrus_l2;
endpackage: folrus_l2;


////////
/*
// for core out / router in
        interface Put#(Flit);
                method Action put(Flit f);
                    if (f.fin_dest != self_addr)
                        begin
                            int destIdx = 0;
                            if(self_addr.L1_headID == f.fin_dest.L1_headID)
                                // destination is in same tile
                                // route to dest
                                destIdx = f.fin_dest.L2_ID;
                            else
                                // destination is in different tile
                                // route to my tile's head
                                destIdx = headIdx;
                            
                            int diffRow = (destIdx / rows) - myRow;
                            int diffCol = (destIdx % rows) - myCol;

                            if(diffRow != 0)
                                if(diffRow > 0)
                                    buffers[linkXPos].enq(f);
                                else
                                    buffers[linkXNeg].enq(f);
                            else
                                if(diffCol > 0)
                                    buffers[linkYPos].enq(f);
                                else
                                    buffers[linkYNeg].enq(f);
                        end
                    else
                        buffers[coreIn].enq(f);
                endmethod
*/