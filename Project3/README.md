Usage:
1. Create a core.bsv file, which has a module named mkCore, satisfying the Ifc_core defined in toplevel_defs.bsv.
2. Create L1Topology.txt and L2Topology.txt in the same format as previously followed
    ```
    L1Topology.txt:
    <Topology>, <Dimension 1>, <Dimension 2><EOF>
    L2Topology.txt:
    <Topology 1>, <Dimension 1 of T1>, <Dimension 2 of T1>
    <Topology 2>, <Dimension 1 of T2>, <Dimension 2 of T2>
    ...
    <Topology n>, <Dimension 1 of Tn>, <Dimension 2 of Tn><EOF>
3. Run generator.py.
4. Run the `runbsvcode` file for simulating.

The team members consider the following as their percentages of contribution. <br>
50% Shashank (EE19B118) <br>
45% Vedaant (CS19B046) <br>
5% Praneeth (CS18B036)


---
Scripts
---
`generator.py`<br>
**requires** &nbsp;`py:re`, &nbsp;&nbsp;`py:networkx`, &nbsp;&nbsp;`core.bsv`, &nbsp;&nbsp;`L1Topology.txt`, &nbsp;&nbsp;`L2Topology.txt`<br>
**features**
- generates the Top-level BSV module as `noc.bsv`.
- utilizes `<topology>_l2.bsv` modules, instantiating based on use as L1, L2 or L2Head nodes.
- robust, warns of any missing files


---
Acknowledgements
---
The following sources were consulted while writing the code:
- Bluespec By Example (Bluespec Inc.)
- Bluespec Reference Guide (Bluespec Inc.)

The following sources constitute part of the codebase:
- Source files (`Makefile`, `runbsvcode`, etc) for simulation provided by Prof. Kamakoti (CSE Dept., IITM)