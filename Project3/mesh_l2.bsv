package mesh_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module mesh_l2#(int n_links, Node_addr self_addr, int rows, int cols, int linkXPos, int linkXNeg, int linkYPos, int linkYNeg) (Ifc_node#(n_links));
    // Only one virtual channel per link, routing is X-Y
    // n_links: 2 (corner) / 3 (edge) / 4 (internal)
    // VC[i] - Link[i]
    // Core will have access to one input and one output buffer

    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //         each IL       for each OL
    Vector#((n_links + 1) * (n_links + 1), FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    $$0

    // the coords of head node in my topology
    int headIdx = (rows / 2) * rows + (col / 2);

    // my coords in the mesh
    int myRow = self_addr.L2_ID / rows;
    int myCol = self_addr.L2_ID % rows;

    // am i a head node?
    bool isHead = $$1;

    // round robin and its incrementer, for router
    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < n_links)
            arbiter_rr_counter <= arbiter_rr_counter + 1
        else
            arbiter_rr_counter <= 0;
    endrule

    $$2

    ////////// Link Rules
    // for each of my links
    for(int i = 0; i < n_links; i++)
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
                                    buffers[n_links * i + linkXPos].enq(f);
                                else
                                    buffers[n_links * i + linkXNeg].enq(f);
                            else if(diffRow != 0)
                                if(diffRow > 0)
                                    buffers[n_links * i + linkYPos].enq(f);
                                else
                                    buffers[n_links * i + linkYNeg].enq(f);
                            $$3
                        end
                        else
                            // its mine, route it to the core
                            buffers[n_links * i].enq(f);
                    end
                endmethod
            endinterface
        endinterface: Ifc_channel
    end

endmodule: mesh_l2;
endpackage: mesh_l2;