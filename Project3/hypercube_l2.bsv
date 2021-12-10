package hypercube_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module hypercube_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int linkDiff2, int linkDiff1, int linkDiff0) (Ifc_node#(n_links));
    // Eight virtual channels per link, routing is via flipping Most Significant Differing Bit
    // n_links: 3 (all)
    // Core will have access to one input and one output buffer

    // buffers for:
    //        links   core  in  out     out VCs
    Vector#((n_links + 1) * (1 + 1) + 7 * n_links, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0
    // up to n_links - 1: ILi
    // n_links to 2n_links - 1: OLi VC0
    // 2n_links to 3n_links - 1: OLi VC1
    // 3n_links to 4n_links - 1: OLi VC2
    // 4n_links to 5n_links - 1: OLi VC3
    // 5n_links to 6n_links - 1: OLi VC4
    // 6n_links to 7n_links - 1: OLi VC5
    // 7n_links to 8n_links - 1: OLi VC6
    // 8n_links to 9n_links - 1: OLi VC7
    // 9n_links: IC
    // 9n_links + 1: OC

    // index of buffers to core
    int coreIn = 9 * n_links;
    int coreOut = 9 * n_links + 1;

    // the coords of head node in my topology
    int headIdx = 0;

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

    Vector#(n_links, Reg#(Int#(3))) arbiter_rr_counters <- replicateM(mkReg(0));
    rule rr_out_incr;
        for(int i = 0; i < n_links; i++)
        begin
            arbiter_rr_counters[i]++;
        end
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
                    int idx = n_links + i + (arbiter_rr_counter[i] * n_links);
                    
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
                        
                        int diff = destIdx ^ self_addr.L2_ID;
                        int offset = destIdx * n_links;

                        if (diff != 0)
                            f.vc = destIdx;

                        if(diff >= 4)
                            buffers[linkDiff2 + offset].enq(f);
                        else if(diff >= 2)
                            buffers[linkDiff1 + offset].enq(f);
                        else if(diff >= 1)
                            buffers[linkDiff0 + offset].enq(f);
                        $$3
                    end
                else
                    // its mine, route it to the core
                    buffers[coreIn].enq(f);
            end
    endrule

endmodule: hypercube_l2;
endpackage: hypercube_l2;