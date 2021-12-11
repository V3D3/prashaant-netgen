package chain_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module chain_l2#(int n_links, Node_addr self_addr, int len, int linkPos, int linkNeg) (Ifc_node#(n_links));
    // Only one virtual channel per link, routing is simple shortest path
    // n_links: 1 (edge) / 2 (internal)
    // Core will have access to one input and one output buffer

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //         each IL       for each OL
    Vector#((n_links + 1) * (n_links + 1), FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0

    // the coords of head node in my topology
    int headIdx = len / 2;

    // my coord: my L2_ID

    // am i a head node?
    bool isHead = $$1;

    $$2

    Reg#(UInt#(2)) arbiter_rr_counter <- mkReg(0);

    rule rr_arbiter_incr;
        if (arbiter_rr_counter < n_links)
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    ////////// Link Rules
    // for each of the links
    for(int i = 0; i <= n_links; i++)
    begin
        // attach to input and output channels
        node_channels[i] = interface Ifc_channel;
            // send flit from me to others
            interface send_flit = toGet(buffers[n_links * arbiter_rr_counter + i]);
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
                            if(self_addr.L1_headID == f.fin_dest.L1_headID)
                                // destination is in same tile
                                // route to dest
                                destIdx = f.fin_dest.L2_ID;
                            
                            int diff = destIdx - self_addr.L2_ID;

                            if(diff > 0)
                                buffers[n_links * i + linkPos].enq(f);
                            else if(diff < 0)
                                buffers[n_links * i + linkNeg].enq(f);
                            $$3
                        end
                        else
                            // its mine, route it to the core
                            buffers[0].enq(f);
                    end
                endmethod
            endinterface
        endinterface: Ifc_channel
    end
endmodule: chain_l2;
endpackage: chain_l2;