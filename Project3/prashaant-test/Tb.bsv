package Tb;

import GetPut::*;
import FIFO::*;
import Connectable::*;

typedef struct  {
	int payload;
} Data deriving(Bits, Eq);

interface Ifc_node#(numeric type link_count);
	interface Vector#(link_count, Ifc_channel) channels;
endinterface

interface Ifc_channel;
	// Input channel - loads filt from the previous node for routing
	interface Put#(Data) load_flit;
	// Output channel - sends flits from the arbiter
	interface Get#(Data) send_flit; 
endinterface	

instance Connectable #(Ifc_channel, Ifc_channel);
	module mkConnection #(Ifc_channel channel_a, Ifc_channel channel_b) (Empty);
		mkConnection (channel_a.send_flit, channel_b.load_flit);
		mkConnection (channel_b.send_flit, channel_a.load_flit);
	endmodule: mkConnection
endinstance: Connectable

module mkA#(int link_count) (Ifc_node#(link_count));
	Vector#(link_count, FIFO#(Data)) buffers <- replicateM(mkFIFO);
	Vector#(link_count, Ifc_channel) temp_channels;
	
	for(int i = 0; i < link_count; i+=1)
	begin
	temp_channels[i] = interface Ifc_channel;
		interface send_flit = toGet(buffers[i]);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				buffers[i].enq(d);
				$display("A got a flit in channel %d", i);
			endmethod
		endinterface;
	endinterface;
	end

	channels = temp_channels;
endmodule

module mkC#(int link_count) (Ifc_node#(link_count));
	Vector#(link_count, FIFO#(Data)) buffers <- replicateM(mkFIFO);
	Vector#(link_count, Ifc_channel) temp_channels;

	rule mygen;
		buffers[1].enq(Data {payload: 69});
	endrule
	
	for(int i = 0; i < link_count; i+=1)
	begin
	temp_channels[i] = interface Ifc_channel;
		interface send_flit = toGet(buffers[i]);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				$display("C got a flit in channel %d", i);
			endmethod
		endinterface;
	endinterface;
	end

	channels = temp_channels;
endmodule


module mkB#(int link_count) (Ifc_node#(link_count));
	Vector#(link_count, FIFO#(Data)) buffers <- replicateM(mkFIFO);
	Vector#(link_count, Ifc_channel) temp_channels;
	
	for(int i = 0; i < link_count; i+=1)
	begin
	temp_channels[i] = interface Ifc_channel;
		interface send_flit = toGet(buffers[i]);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				buffers[1 - i].enq(d);
				$display("C got a flit in channel %d", i);
			endmethod
		endinterface;
	endinterface;
	end

	channels = temp_channels;
endmodule

(* synthesize *)

module mkTb(Empty);
	Ifc_node#(2) a <- mkA#(2);
	Ifc_node#(2) b <- mkB#(2);
	Ifc_node#(2) c <- mkC#(2);

	mkConnection(a.channels[0], b.channels[0]);
	mkConnection(b.channels[1], c.channels[1]);
endmodule: mkTb

endpackage: Tb
