package Tb;

import GetPut::*;
import FIFO::*;
import Connectable::*;

typedef struct  {
	int payload;
} Data deriving(Bits, Eq);

interface Ifc_node;
	interface Ifc_channel channel;
endinterface
interface Ifc_node2;
	interface Ifc_channel channel1;
	interface Ifc_channel channel2;
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

module mkA(Ifc_node);
	FIFO#(Data) myfifo <- mkFIFO;

	interface channel = interface Ifc_channel;
		interface send_flit = toGet(myfifo);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				myfifo.enq(d);
				$display("A got a flit");
			endmethod
		endinterface;
	endinterface;
endmodule

module mkB(Ifc_node);
	FIFO#(Data) myfifo <- mkFIFO;

	rule mygen;
		myfifo.enq(Data {payload: 69});
	endrule

	interface channel = interface Ifc_channel;
		interface send_flit = toGet(myfifo);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				$display("B got a flit");
			endmethod
		endinterface;
	endinterface;
endmodule

module mkC(Ifc_node2);
	FIFO#(Data) myfifo1 <- mkFIFO;
	FIFO#(Data) myfifo2 <- mkFIFO;

	interface channel1 = interface Ifc_channel;
		interface send_flit = toGet(myfifo1);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				myfifo2.enq(d);
				$display("C got a flit in 1, put in 2");
			endmethod
		endinterface;
	endinterface;

	interface channel2 = interface Ifc_channel;
		interface send_flit = toGet(myfifo2);
		interface load_flit = interface Put#(Data);
			method Action put(Data d);
				myfifo1.enq(d);
				$display("C got a flit in 2, put in 1");
			endmethod
		endinterface;
	endinterface;
endmodule

(* synthesize *)

module mkTb(Empty);
	Ifc_node a <- mkA;
	Ifc_node b <- mkB;
	Ifc_node2 c <- mkC;

	mkConnection(a.channel, c.channel1);
	mkConnection(c.channel2, b.channel);

	rule greet;
		$display ("Hello World");
	endrule
endmodule: mkTb

endpackage: Tb
