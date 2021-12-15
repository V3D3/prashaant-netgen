package Tb;

import GetPut::*;
import FIFO::*;
import Connectable::*;

typedef struct  {
	int payload;
} Data deriving(Bits, Eq);

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

module mkA(Ifc_channel);
	FIFO#(Data) myfifo <- mkFIFO;

	rule mygen;
		myfifo.enq(Data {payload: 123});
	endrule

	interface send_flit = toGet(myfifo);
	interface load_flit = interface Put#(Data);
		method Action put(Data d);
			myfifo.enq(d);
			$display("A got a flit");
		endmethod
	endinterface;
endmodule

module mkB(Ifc_channel);
	FIFO#(Data) myfifo <- mkFIFO;

	rule mygen;
		myfifo.enq(Data {payload: 69});
	endrule

	interface send_flit = toGet(myfifo);
	interface load_flit = interface Put#(Data);
		method Action put(Data d);
			myfifo.enq(d);
			$display("B got a flit");
		endmethod
	endinterface;
endmodule

(* synthesize *)

module mkTb(Empty);
	Ifc_channel a <- mkA;
	Ifc_channel b <- mkB;

	mkConnection(a, b);

	rule greet;
		$display ("Hello World");
	endrule
endmodule: mkTb

endpackage: Tb
