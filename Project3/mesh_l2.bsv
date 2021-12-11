package mesh_l2;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module mesh_l2#(int n_links, Node_addr self_addr, int rows, int cols, int linkXPos, int linkXNeg, int linkYPos, int linkYNeg, Bool isHead, Bool isL1) (Ifc_node#(n_links));
    // Only one virtual channel per link, routing is X-Y
    // n_links: 2 (corner) / 3 (edge) / 4 (internal)
    // Core will have access to one input and one output buffer

    int link_count = n_links + 1;
    if (isHead)
        link_count = link_count + 1;

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
    //         each IL       for each OL
    Vector#(link_count * link_count, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // the coords of head node in my topology
    int headIdx = (rows / 2) * rows + (col / 2);

    // my coords in the mesh
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
    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)
            arbiter_rr_counter <= arbiter_rr_counter + 1
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a headrouter
    //      => I am either a non-head node (start: 1)
    //         or a head node (start: 2)
    if (!isL1)
    begin
        for(int i = 0; i < link_count; i++)
        begin
            // attach to input and output channels
            node_channels[i] = interface Ifc_channel;
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit);
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
                            // route it to an output buffer, if not mine
                            if (f.fin_dest != self_addr)
                            begin
                                // assume dest is in different tile, route to head
                                int destIdx = headIdx;
                                if(self_addr.l1_headID == f.fin_dest.l1_headID)
                                    // destination is in same tile
                                    // route to dest
                                    destIdx = f.fin_dest.l2_ID;
                                
                                int diffRow = (destIdx / rows) - myRow;
                                int diffCol = (destIdx % rows) - myCol;

                                if (diffCol != 0)
                                    if(diffCol > 0)
                                        buffers[link_count * i + linkXPos].enq(f);
                                    else
                                        buffers[link_count * i + linkXNeg].enq(f);
                                else if(diffRow != 0)
                                    if(diffRow > 0)
                                        buffers[link_count * i + linkYPos].enq(f);
                                    else
                                        buffers[link_count * i + linkYNeg].enq(f);
                                else
                                    // it must go outwards, to L1 routing
                                    if (isHead)
                                        buffers[link_count * i + 1].enq(f);
                                    else
                                        // Error!
                                        $display("error: mesh_l2.bsv:108");
                            end
                            else
                                // its mine, route it to the core
                                buffers[link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end
    else
    begin
        for(int i = 0; i < link_count; i++)
        begin
            // attach to input and output channels
            node_channels[i] = interface Ifc_channel;
                // send flit from me to others
                interface send_flit = toGet(buffers[link_count * arbiter_rr_counter + i]);
                // receive a flit from somewhere
                interface load_flit = interface Put#(Flit);
                    method Action put(Flit f);
                        // is the flit useful?
                        if(f.valid == 1)
                        begin
                            int destIdx = f.fin_dest.l1_headID;
                            
                            int diffRow = (destIdx / rows) - myRow;
                            int diffCol = (destIdx % rows) - myCol;

                            if (diffCol != 0)
                                if(diffCol > 0)
                                    buffers[link_count * i + linkXPos].enq(f);
                                else
                                    buffers[link_count * i + linkXNeg].enq(f);
                            else if(diffRow != 0)
                                if(diffRow > 0)
                                    buffers[link_count * i + linkYPos].enq(f);
                                else
                                    buffers[link_count * i + linkYNeg].enq(f);
                            else
                                // its my tile's, route it to my node, for L2 routing
                                buffers[link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end

endmodule: mesh_l2;
endpackage: mesh_l2;