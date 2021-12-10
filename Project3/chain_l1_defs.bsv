    Vector#(%n_headbuffers%, FIFO#(Flit)) headbuffers <- replicateM(mkFIFO);
$$$
true
$$$
// first, we create the rr counter for router
    Reg#(int) router_rr_counter_head <- mkReg(0);
    rule rr_in_incr_head;
        if(router_rr_counter_head == %n_links%)
            router_rr_counter_head <= 0
        else
            router_rr_counter_head <= router_rr_counter_head + 1;
    endrule
// next, we satisfy the channel interface for head's node_channels
    for(int i = n_links; i < n_links + %n_links%; i++)
    begin
        node_channels[i] = interface Ifc_channel;
            interface send_flit = toGet(headbuffers[%n_links% + i]);
            interface load_flit = toPut(headbuffers[i]);
        endinterface
    end
// finally we add rules for head's input to output links, with additionally enqueing to node's own buffers if needed
    rule il_to_router_rr_head;
        Flit f = buffers[router_rr_counter_head].first();
        buffers[router_rr_counter_head].deq();

        if(f.valid == 1)
        begin
            if(f.fin_dest.L1_headID != self_addr.L1_headID)
            begin
                int destIdx = f.fin_dest.L1_headID;
                int diff = destIdx - self_addr.L1_headID;

                if(diff > 0)
                    headbuffers[%linkPos%].enq(f);
                else
                    headbuffers[%linkNeg%].enq(f);
            end
            else
                // use coreOut as a universal means of transferring from L1 to L2 routing
                buffers[coreOut].enq(f);
        end
    endrule
$$$
                        else
                            // destination is in different tile, and this is a head tile
                            // so we're routing in L1
                            // NOTE: this occurs only 1 time - when flit is on the head node of the first tile
                            //       thereafter, the ILs used are different
                            begin
                                int headDestIdx = f.fin_dest.L1_headID;

                                int hdiff = headDestIdx - self_addr.L1_headID;

                                if (diff > 0)
                                    headbuffers[%linkPos%].enq(f);
                                else
                                    headbuffers[%linkNeg%].enq(f);
                            end