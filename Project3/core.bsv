/****************************************************************
****************** SAMPLE CORE***********************************
*****************************************************************

This is a sample core that has been used for simulation purposes.
Random generator adopted from Bluespec Inc. reference guide

****************************************************************
***************************************************************/

package core;

import toplevel_defs::*;
import GetPut::*;
import FIFO::*;
import LFSR::*;


module mkCore(Ifc_core);

  // LFSR for generating random numbers
  LFSR#(Bit#(8)) lfsr <- mkLFSR_8;
  
  // A FIFO to store the flit generated by the Core
  FIFO#(Flit) generated_flit <- mkFIFO();

  Reg#(int) count <- mkReg(0);
  

  // Keep counting
  rule counting;
    count <= count + 1;
    lfsr.next;
  endrule

  // The following action occurs at random time (25% probability now)
  rule action2 (lfsr.value() > 192);
      // Modify this so that it generates random flits with the constraints set by the actual network
      $display("Generated a flit");
      generated_flit.enq( Flit {valid : 1, src : Node_addr {l1_headID : 0, l2_ID : 0}, fin_dest : Node_addr {l1_headID : 1, l2_ID : 1}, payload : 0, vc: 0 });  
  endrule
  
  interface send_flit = toGet(generated_flit);
  interface load_flit = interface Put#(Flit);
                          method Action put(Flit f);
                            // This flit can be handled by the code
                            $display("A flit has been successfully consumed by a core");
                          endmethod
                        endinterface;
          
endmodule: mkCore

endpackage: core