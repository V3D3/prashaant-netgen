package noc;

import Vectors::*;
import toplevel_defs::*;
import GetPut::*;

// example for:
// L1 C,3,1
// L2 all H,8,8

module noc (Empty);
    Ifc_core c0_0 <- mkCore;
    Ifc_node n0_0 <- hypercube_l2#(3, Node_addr {l1_headID: 0, l2_ID: 0}, c0_0, 0, 1, 2);
    ... for c0_1, n0_1... upto c0_7, n0_7
    ... then for c1_0, n1_0... upto c7_7, n7_7

    // now make connections
    mkConnection(n0_0.node_channels[2], n0_1.node_channels[2]);
    mkConnection(n0_0.node_channels[1], n0_2.node_channels[1]);
    mkConnection(n0_0.node_channels[0], n0_4.node_channels[0]);
    ... for n0_i with bit differences from i...

    // now make L1 connections
    mkConnection(n0_0.node_channels[3], n1_0.node_channels[3]);
    mkConnection(n1_0.node_channels[4], n2_0.node_channels[3]);

    // simulate?
endmodule: noc

endpackage: noc