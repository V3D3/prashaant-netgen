package butterfly_l2_node;

import Vectors::*;
import toplevel_defs ::*;
import GetPut::*;


module butterfly_l2_node#(int k, Ifc_core core, Node_addr self_addr, Bool isL1)(Ifc_node#(n_links));

  // Checks if the node is on the head side
  Bit#(1) head_side = (self_addr.l2_ID < 2**k)?1:0;
  
  // am I a head node?
  Bool isHead = $$1;
  
  // the coords of head node in my topology
  int headIdx = 0;
  
  // Treat core as a channel (IL / OL)
  // A non head butterfly node will have only a single channel that connects it to a switch. Including 1 buffer for the core, we require 2 buffers
  

  // The routers would store flits into the corresponding buffers, and the arbiter picks and transmits flits from its set of buffers in a round-robin fashion
	
	// Buffers for the L2 routing/ channels
	Vector#((n_links + 1)*(n_links + 1), FIFO#(Flit)) buff_vc <- replicateM(mkFIFO());     // buff_vc[0] is for the input link, and buff_vc[1] is for the core
	$$0
	
	
	
	// Register to store the Round robin Count for the single internal output link
	Reg#(int) round_robin <- mkReg(0);

	// Rule to get the flits from the Core
	
	rule get_core_flit;
	
		if core.gen_Flit                                 /// this rule to be handled
	
	endrule

	// Rules to update the Round Robin counter
	rule round_robin_count;

		// Reset the counter to the initial position after one interation of going around the buffers

		if (round_robin_1 == 1) round_robin <= 0;
		else 			round_robin <= 1;

	endrule






	// Interface definitions

	channel[0] = interface Ifc_channel;
			interface send_flit = toGet(buff_vc[round_robin_1]);

	// A flit that comes in to a node in butterfly has to be consumed unless it is a head node
	
			interface load_flit = interface Put#(Flit);   // check how to add int for VC (previous node should pass this) 
							method Action put(Flit f);
								if (f.fin_dest ! = self_addr)
									$display("Illegal routing. This node cannot be accessed");
									core.
								else
								
							endmethod
					     endinterface;


    int link_count = n_links + 1;

    if (isHead)
        link_count = link_count + 1;

    // Actual node links depend on the cases:
    // this is a non-head node: 0: core, 1: node and so on
    // this is a head node: 0: core, 1: headrouter, 2: node and so on
    // this is a head router (L1): 0: my node, 1: other headnode, 2: other headnode and so on
    int nodelink_start = 1;
    
    if (isHead)
    begin
        nodelink_start = 2;
    end
    
    
    // buffers for:
    // (core is treated as an IL/OL, it is at 0)
    //       each IL    for each OL
    Vector#(link_count * link_count, FIFO#(Flit)) buffers <- replicateM(mkFIFO);

    // the coords of head node in my topology
    int headIdx = 0;

    // my coord: my L2_ID

    Reg#(UInt#(3)) arbiter_rr_counter <- mkReg(0);
    rule rr_arbiter_incr;
        if (arbiter_rr_counter < link_count - 1)                      
            arbiter_rr_counter <= arbiter_rr_counter + 1;
        else
            arbiter_rr_counter <= 0;
    endrule

    // Link Rules
    // Case: I am not a L1 headrouter
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
                                // assume destination is in different tile, route to head
                                int destIdx = headIdx;
                                if(self_addr.l1_headID == f.fin_dest.l1_headID)
				begin
                                    // destination is in same tile
                                    // route to dest
                                    destIdx = f.fin_dest.l2_ID;
				    
       	                            buffers[link_count * i].enq(f);
         			 end
				    

				 else
                                    // it must go outwards, to L1 routing
                                    if (isHead)
                                        buffers[link_count * i + 1].enq(f);
                                    else
                                        // Error!
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
    // Case: I am a L1 head router (start: 1)
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
			    if(f.fin_dest.l1_headID != self_addr.l1_headID)
       	                            buffers[link_count * i].enq(f);				    
                            else
                                // its mine, route it to the node for internal routing
                                buffers[2*link_count * i].enq(f);
                        end
                    endmethod
                endinterface
            endinterface: Ifc_channel
        end
    end




endmodule

endpackage
