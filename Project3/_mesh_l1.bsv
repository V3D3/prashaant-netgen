/*** DONT USE ME, I am just a model for generated head node bsv files ***/

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;

module mesh_l2#(int n_links, Node_addr self_addr, Ifc_core tile, int rows, int cols, int linkXPos, int linkXNeg, int linkYPos, int linkYNeg) (Ifc_node#(n_links));
    // Only one virtual channel per link, routing is X-Y
    // n_links: 2 (corner) / 3 (edge) / 4 (internal)
    // VC[i] - Link[i]
    // Core will have access to one input and one output buffer

    // buffers for:
    //        links   core  in  out
    Vector#((n_links + 1) * (1 + 1), FIFO#(Flit)) buffers <- replicateM(mkFIFO);
    // $$0
    Vector#(<somecount>, FIFO#(Flit)) headbuffers <- replicateM(mkFIFO);
    // up to n_links - 1: ILi
    // n_links to 2n_links - 1: OLi
    // 2n_links: IC
    // 2n_links + 1: OC

    // index of buffers to core
    int coreIn = 2 * n_links;
    int coreOut = 2 * n_links + 1;

    // the coords of head node in my topology
    int headIdx = (rows / 2) * rows + (col / 2);

    // my coords in the mesh
    int myRow = self_addr.l2_ID / rows;
    int myCol = self_addr.l2_ID % rows;

    // am i a head node?
    bool isHead = true; // $$1

    // round robin and its incrementer, for router
    Reg#(int) router_rr_counter <- mkReg(0);
    rule rr_out_incr;
        if (router_rr_counter == n_links + 1)
            router_rr_counter <= 0
        else
            router_rr_counter <= router_rr_counter + 1;
    endrule;

    // $$2
    Reg#(int) router_rr_counter_head <- mkReg(0);
    rule...
    endrule

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

    for(int i = 0; i < extra_links; i++)
    begin

    end

    ////////// Router rules
    // BI/ILx to OLx/BO buffers
    rule il_to_router_rr;
        // for each ILi / router in
        Flit f;
        if (router_rr_counter == n_links)
            // use BO
            begin
                f = buffers[coreOut].first();
                buffers[coreOut].deq();
            end
        else
            // use IL
            begin
                // get the flit from input
                f = buffers[router_rr_counter].first();
                buffers[router_rr_counter].deq();
            end
        
        // is the flit useful?
        if(f.valid == 1)
            begin
                // route it to an output buffer, if not mine
                if (f.fin_dest != self_addr)
                    begin
                        int destIdx = 0;
                        if(self_addr.l1_headID == f.fin_dest.l1_headID)
                            // destination is in same tile
                            // route to dest
                            destIdx = f.fin_dest.l2_ID;
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
                    // its mine, route it to the core
                    buffers[coreIn].enq(f);
            end
    endrule


    //////////// We'll let the core decide when it wants to consume from coreIn and let it manage coreIn
    // rule core_consume;
    //     Flit f = buffers[coreIn].first();
    //     buffers[coreIn].deq();

    //     if(f.valid == 1)
    //         begin
    //             core.consume_flit(f);
    //         end
    // endrule

endmodule: mesh_l2;
endpackage: mesh_l2;


////////
/*
// for core out / router in
        interface Put#(Flit);
                method Action put(Flit f);
                    if (f.fin_dest != self_addr)
                        begin
                            int destIdx = 0;
                            if(self_addr.l1_headID == f.fin_dest.l1_headID)
                                // destination is in same tile
                                // route to dest
                                destIdx = f.fin_dest.l2_ID;
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