Usage:
1. Create a core.bsv file, which has a module named mkCore, satisfying the Ifc_core defined in toplevel_defs.bsv.
2. Create L1Topology.txt and L2Topology.txt in the same format as previously followed
    L1Topology.txt:
    <Topology>, <Dimension 1>, <Dimension 2><EOF>
    L2Topology.txt:
    <Topology 1>, <Dimension 1 of T1>, <Dimension 2 of T1>
    <Topology 2>, <Dimension 1 of T2>, <Dimension 2 of T2>
    ...
    <Topology n>, <Dimension 1 of Tn>, <Dimension 2 of Tn><EOF>
3. Run generator.py.
4. Run the created runbsvcode file.

The team members consider the following as their percentages of contribution.
50% Shashank (EE19B118)
45% Vedaant (CS19B046)
5% Praneeth (CS18B036)


---
Readme for Developers
---
`generator.py`<br>
**requires** &nbsp;`py:re`, &nbsp;&nbsp;`core.bsv`, &nbsp;&nbsp;`L1Topology.txt`, &nbsp;&nbsp;`L2Topology.txt`<br>
**features**
- generates the Top-level BSV module as `noc.bsv`.
- utilizes `<topology>_l2.bsv` files as L2 node file blueprints.
- plugs in code from `<topology>_l1_defs.bsv` files as L1 functionality for head nodes, in corresponding L2 node file
- references are defined in L2 files as `$$<index>`, referrng to sections in defs file separated by `$$$`, 0-indexed.
- robust, warns of any missing files

