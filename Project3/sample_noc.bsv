// Sample noc.bsv for C 3,1 C 3,1 C 3,1
package noc;

import toplevel_defs::*;
import core::*;

import Connectable::*;

import chain_l2::*;
import ring_l2::*;
import mesh_l2::*;
import folrus_l2::*;
//import butterfly_l2::*;
import hypercube_l2::*;

module noc (Empty);


 // [1/5] Adding instantiation of L1 (Head Router) Nodes 

        Ifc_node#(3) n0 <- chain_l2(3, Node_addr {l1_headID: 0, l2_ID: 999}, 3, 1, 2, False, True);
        Ifc_node#(3) n1 <- chain_l2(3, Node_addr {l1_headID: 1, l2_ID: 999}, 3, 1, 2, False, True);
        Ifc_node#(3) n2 <- chain_l2(3, Node_addr {l1_headID: 2, l2_ID: 999}, 3, 1, 2, False, True);


 // [2/5] Adding edges between L1 (Head Router) Nodes 

        mkConnection(n0.node_channels[1], n1.node_channels[2]);
        mkConnection(n1.node_channels[1], n2.node_channels[2]);


 // [3/5] Adding instantiation of L2 Nodes 



 // L2 Generation : Class: C, HeadID: 0

        Ifc_node#(3) nI0Z0 <- chain_l2(3, Node_addr {l1_headID: 0, l2_ID: 0}, 3, 1, 2, False, False);
        Ifc_node#(4) nO0Z1 <- chain_l2(4, Node_addr {l1_headID: 0, l2_ID: 1}, 3, 1, 2, True, False);
        Ifc_node#(3) nI0Z2 <- chain_l2(3, Node_addr {l1_headID: 0, l2_ID: 2}, 3, 1, 2, False, False);


 // L2 Generation : Class: C, HeadID: 1

        Ifc_node#(3) nI1Z0 <- chain_l2(3, Node_addr {l1_headID: 1, l2_ID: 0}, 3, 1, 2, False, False);
        Ifc_node#(4) nO1Z1 <- chain_l2(4, Node_addr {l1_headID: 1, l2_ID: 1}, 3, 1, 2, True, False);
        Ifc_node#(3) nI1Z2 <- chain_l2(3, Node_addr {l1_headID: 1, l2_ID: 2}, 3, 1, 2, False, False);


 // L2 Generation : Class: C, HeadID: 2

        Ifc_node#(3) nI2Z0 <- chain_l2(3, Node_addr {l1_headID: 2, l2_ID: 0}, 3, 1, 2, False, False);
        Ifc_node#(4) nO2Z1 <- chain_l2(4, Node_addr {l1_headID: 2, l2_ID: 1}, 3, 1, 2, True, False);
        Ifc_node#(3) nI2Z2 <- chain_l2(3, Node_addr {l1_headID: 2, l2_ID: 2}, 3, 1, 2, False, False);


 // [4/5] Adding edges between L2 Nodes 



        // L2 Generation : Class: C, HeadID: 0

        mkConnection(nI0Z0.node_channels[1], nO0Z1.node_channels[3]);
        mkConnection(nO0Z1.node_channels[2], nI0Z2.node_channels[2]);


        // L2 Generation : Class: C, HeadID: 1

        mkConnection(nI1Z0.node_channels[1], nO1Z1.node_channels[3]);
        mkConnection(nO1Z1.node_channels[2], nI1Z2.node_channels[2]);


        // L2 Generation : Class: C, HeadID: 2

        mkConnection(nI2Z0.node_channels[1], nO2Z1.node_channels[3]);
        mkConnection(nO2Z1.node_channels[2], nI2Z2.node_channels[2]);


 // [5/5] Adding instantiation of cores; linking cores and routers to nodes 



        // L2 Generation : Class: C, HeadID: 0

        Ifc_core cI0Z0 <- mkCore(Node_addr {l1_headID: 0, l2_ID: 0});
        mkConnection(cI0Z0, nI0Z0.node_channels[0]);
        Ifc_core cO0Z1 <- mkCore(Node_addr {l1_headID: 0, l2_ID: 1});
        mkConnection(cO0Z1, nO0Z1.node_channels[0]);
        mkConnection(n0.node_channels[0], nO0Z1.node_channels[1]);
        Ifc_core cI0Z2 <- mkCore(Node_addr {l1_headID: 0, l2_ID: 2});
        mkConnection(cI0Z2, nI0Z2.node_channels[0]);


        // L2 Generation : Class: C, HeadID: 1

        Ifc_core cI1Z0 <- mkCore(Node_addr {l1_headID: 1, l2_ID: 0});
        mkConnection(cI1Z0, nI1Z0.node_channels[0]);
        Ifc_core cO1Z1 <- mkCore(Node_addr {l1_headID: 1, l2_ID: 1});
        mkConnection(cO1Z1, nO1Z1.node_channels[0]);
        mkConnection(n1.node_channels[0], nO1Z1.node_channels[1]);
        Ifc_core cI1Z2 <- mkCore(Node_addr {l1_headID: 1, l2_ID: 2});
        mkConnection(cI1Z2, nI1Z2.node_channels[0]);


        // L2 Generation : Class: C, HeadID: 2

        Ifc_core cI2Z0 <- mkCore(Node_addr {l1_headID: 2, l2_ID: 0});
        mkConnection(cI2Z0, nI2Z0.node_channels[0]);
        Ifc_core cO2Z1 <- mkCore(Node_addr {l1_headID: 2, l2_ID: 1});
        mkConnection(cO2Z1, nO2Z1.node_channels[0]);
        mkConnection(n2.node_channels[0], nO2Z1.node_channels[1]);
        Ifc_core cI2Z2 <- mkCore(Node_addr {l1_headID: 2, l2_ID: 2});
        mkConnection(cI2Z2, nI2Z2.node_channels[0]);

endmodule: noc

endpackage: noc
