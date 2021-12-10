package folrus_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module folrus_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int rows, int cols, int linkXPos, int linkXNeg, int linkYPos, int linkYNeg) (Ifc_node#(n_links));
    // Two virtual channels per link, routing is X (for locating ring, shortest arc), then Date-line in Y
    // n_links: 4 (all)
    // Core will have access to one input and one output buffer

    // buffers for:
    //        links   core  in  out   out VC1s
    Vector#((n_links + 1) * (1 + 1) + n_links, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0
    // up to n_links - 1: ILi
    // n_links to 2n_links - 1: OLi VC0
    // 2n_links to 3n_links - 1: OLi VC1
    // 3n_links: IC
    // 3n_links + 1: OC

    // index of buffers to core
    int coreIn = 3 * n_links;
    int coreOut = 3 * n_links + 1;

    // the coords of head node in my topology
    int headIdx = 0;

    // my coords in the FT
    int myRow = self_addr.L2_ID / rows;
    int myCol = self_addr.L2_ID % rows;

    // am i a head node?
    bool isHead = $$1;

    // round robin and its incrementer, for router
    Reg#(int) router_rr_counter <- mkReg(0);
    rule rr_in_incr;
        if (router_rr_counter == n_links + 1)
            router_rr_counter <= 0
        else
            router_rr_counter <= router_rr_counter + 1;
    endrule

    // bits to indicate VC serviced by arbiter (roundrobin fashion)
    Reg#(Bit#(n_links)) arbiter_rr_counters <- mkReg(0);
    rule rr_out_incr;
        arbiter_rr_counters <= ~arbiter_rr_counters;
    endrule

    $$2

    ////////// Link Rules
    // for each of my links
    for(int i = 0; i < n_links; i++)
    begin
        // attach to input and output channels
        node_channels[i] = interface Ifc_channel;
            // send flit from me to others
            interface send_flit = interface Get#(Flit);
                method ActionValue get();
                    int idx = n_links + i;
                    if (arbiter_rr_counters[i] == 1)
                        idx = idx + n_links;
                    
                    buffers[idx].deq();
                    return buffers[idx].first();
                endmethod
            endinterface
            // receive a flit from somewhere
            interface load_flit = toPut(buffers[i]);
        endinterface: Ifc_channel
    end

    ////////// Router rules
    // BI/ILx to OLx/BO buffers
    rule il_to_router_rr;
        // for each ILi / router in
        Flit f;
        // use IL by default
        int idx = router_rr_counter;
        if (router_rr_counter == n_links)
            // use CoreOut
            idx = coreOut;
        
        f = buffers[idx].first();
        buffers[idx].deq();
        
        // is the flit useful?
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

                        if(diffRow != 0)
                            if(diffRow > 0)
                                buffers[linkXPos].enq(f);
                            else
                                buffers[linkXNeg].enq(f);
                        else if (diffCol != 0)
                            begin
                                int idx = linkYPos;
                                if ((f.vc == 1) || (myCol == 1))
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
                    buffers[coreIn].enq(f);
            end
    endrule

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