package chain_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module chain_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int len, int linkPos, int linkNeg) (Ifc_node#(n_links));
    // Only one virtual channel per link, routing is simple shortest path
    // n_links: 1 (edge) / 2 (internal)
    // Core will have access to one input and one output buffer

    // buffers for:
    //        links   core  in  out
    Vector#((n_links + 1) * (1 + 1), FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0
    // up to n_links - 1: ILi
    // n_links to 2n_links - 1: OLi
    // 2n_links: IC
    // 2n_links + 1: OC

    // index of buffers to core
    int coreIn = 2 * n_links;
    int coreOut = 2 * n_links + 1;

    // the coords of head node in my topology
    int headIdx = len / 2;

    // my coord: my L2_ID

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

    $$2

    ////////// Link Rules
    // for each of my links
    for(int i = 0; i < n_links; i++)
    begin
        // attach to input and output channels
        node_channels[i] = interface Ifc_channel;
            // send flit from me to others
            interface send_flit = toGet(buffers[n_links + i]);
            // receive a flit from somewhere
            interface load_flit = toPut(buffers[i]);
        endinterface: Ifc_channel
    end

    ////////// Router rules
    // BI/ILx to OLx/BO buffers
    rule il_to_router_rr;
        // for each ILi / router in

        // use IL by default
        int idx = router_rr_counter;
        if (router_rr_counter == n_links)
            // use CoreOut
            idx = coreOut;

        Flit f = buffers[idx].first();
        buffers[idx].deq();
        
        // is the flit useful?
        if(f.valid == 1)
            begin
                // route it to an output buffer, if not mine
                if (f.fin_dest != self_addr)
                    begin
                        // assume destination is in different tile, route to head
                        int destIdx = headIdx;
                        if(self_addr.L1_headID == f.fin_dest.L1_headID)
                            // destination is in same tile
                            // route to dest
                            destIdx = f.fin_dest.L2_ID;
                        
                        int diff = destIdx - self_addr.L2_ID;

                        if(diff > 0)
                            buffers[linkPos].enq(f);
                        else if(diff < 0)
                            buffers[linkNeg].enq(f);
                        $$3
                    end
                else
                    // its mine, route it to the core
                    buffers[coreIn].enq(f);
            end
    endrule

endmodule: chain_l2;
endpackage: chain_l2;