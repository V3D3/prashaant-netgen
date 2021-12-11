// Random generator adopted from Bluespec Inc. reference guide

import common_defs::*;

module mkCore(Ifc_core)

LFSR#(Bit#(8)) lfsr <- mkLFSR_8 i_rand;

// Keep counting
rule counting;
  count <= count + 1;
  lfsr.next;
endrule



endmodule
