package hypercube_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module hypercube_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int linkDiff2, int linkDiff1, int linkDiff0) (Ifc_node#(n_links));
    // Eight virtual channels per link, routing is via flipping Most Significant Differing Bit
    // n_links: 3 (all)
    // Core will have access to one input and one output buffer

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //         each IL       for each OL   VCs
    Vector#((n_links + 1) * (n_links + 1) * 8, FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0
    // up to n_links - 1: ILi
    
    // we have (n_links + 1) buckets of size (n_links + 1) * 8
    // one bucket per IL
    // each bucket has 8 sections, each of size (n_links + 1)
    // one section per VC
    // each section has n_links + 1 FIFOs
    // one FIFO per OL

    // the coords of head node in my topology
    int headIdx = 0;

    // my coord: my L2_ID

    // am i a head node?
    bool isHead = $$1;

    // round robin and its incrementer, for arbiter
    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    Reg#(UInt#(3)) arbiter_rr_vc_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < n_links)
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

    $$2

    ////////// Link Rules
    // for each of my links
    for(int i = 0; i <= n_links; i++)
    begin
        // attach to input and output channels
        node_channels[i] = interface Ifc_channel;
            // send flit from me to others
            interface send_flit = toGet(buffers[8 * n_links * arbiter_rr_counter
                                            +   n_links * arbiter_rr_vc_counter
                                            +   i]);
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
                            
                            int diff = destIdx ^ self_addr.L2_ID;
                            int offset = destIdx * n_links;

                            if (diff != 0)
                                f.vc = destIdx;

                            if(diff >= 4)
                                buffers[8 * n_links * i + linkDiff2 + offset].enq(f);
                            else if(diff >= 2)
                                buffers[8 * n_links * i + linkDiff1 + offset].enq(f);
                            else if(diff >= 1)
                                buffers[8 * n_links * i + linkDiff0 + offset].enq(f);
                            $$3
                        end
                        else
                            // its mine, route it to the core
                            buffers[8 * n_links * i].enq(f);
                    end
                endmethod
            endinterface
        endinterface: Ifc_channel
    end

endmodule: hypercube_l2;
endpackage: hypercube_l2;