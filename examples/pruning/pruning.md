# Pruning Example: DFN Generation, Graph Analysis, and Pruning

**Version:** 2.9.5 
**Maintainer:** Jeffrey Hyman  
**Author:** Jeffrey Hyman <jhyman@lanl.gov>  
**Date:** 18 Nov 2025

---

## Synopsis

This example demonstrates the complete workflow for **Discrete Fracture Network (DFN)** generation, analysis, and pruning using a **Truncated Power Law (TPL)** fracture size distribution with `pydfnworks`.  

The script shows how to:
- Configure the DFN domain and simulation parameters  
- Define multiple fracture families following a TPL distribution  
- Generate a 3D DFN and create a graph representation of its connectivity  
- Identify and extract the **hydraulic backbone** (the main flow-connected network)  
- Prune the DFN to retain only fractures belonging to the backbone  
- Save and reload the DFN state from a pickle file  
- Mesh the pruned backbone for further numerical simulations  

---

## How to Run

To execute this example, ensure that `pydfnworks` and its dependencies are properly installed and your environment is configured.

From the command line, run:

```bash
python driver.py


## Workflow Summary

1. **Initialize the DFN**  
   Set domain size, resolution, and boundary conditions using the `DFNWORKS` class.

2. **Add Fracture Families**  
   Use truncated power-law (TPL) distributions to define fracture size and hydraulic aperture.

3. **Generate the DFN**  
   Create the fracture network and visualize it.

4. **Construct the Flow Network**  
   Build a graph representation of the DFN and identify dead-end or non-flowing features.

5. **Extract and Prune the Backbone**  
   Identify the flow backbone, remove isolated fractures, and save the pruned network.

6. **Rebuild and Mesh the Pruned DFN**  
   Load the pruned data into a new DFN object, regenerate working directories, and mesh for downstream simulation.

---

## Key Features Demonstrated

- Integration of geometry generation, network analysis, and meshing workflows  
- Use of the **TPL distribution** for fracture scaling  
- Graph-based connectivity and backbone extraction using `networkx`  
- Regeneration and meshing of a pruned DFN for flow simulations  

---

## References

This example is part of the `pydfnworks` tutorial suite and illustrates a realistic DFN workflow suitable for hydraulic and transport modeling.

