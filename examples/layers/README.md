# Layer-Conforming Fracture Truncation Example

This example demonstrates the `layerConformingFractures` feature in dfnGen, which controls how stochastic fractures interact with layer boundaries.

## Background

When a DFN domain is divided into layers, fracture *centers* are always sampled within their assigned layer. Without conforming, however, fracture *polygons* can extend freely into adjacent layers — a large fracture centered near a layer boundary will cross it. Depending on your application this may be physically unrealistic (e.g., a low-permeability aquitard separating two aquifers should not be penetrated by fractures assigned to either aquifer).

The `layerConformingFractures` parameter gives you three options:

| Mode | Value | Behavior |
|------|-------|----------|
| Disabled | `0` | Fractures extend freely beyond layer boundaries (legacy behavior) |
| Perfect conforming | `1` | Fractures are clipped exactly at the layer Z boundaries |
| Soft conforming | `2` | Fractures are clipped at the layer boundary ± 2h |

Mode 2 is recommended for most applications. Perfect conforming (mode 1) can disconnect the network at layer interfaces because fractures from adjacent layers, each clipped exactly to their own boundary, share no geometric overlap at the interface plane. The 2h overhang in mode 2 preserves that overlap and maintains flow connectivity across the boundary.

## Domain Setup

```
z =  5.0  ┌─────────────────────┐  ← +Z domain boundary
           │                     │
           │   Layer 2 (top)     │  family 2, p32 = 4
           │                     │
z =  0.0  ├─────────────────────┤  ← layer interface
           │                     │
           │   Layer 1 (bottom)  │  family 1, p32 = 4
           │                     │
z = -5.0  └─────────────────────┘  ← -Z domain boundary
```

- Domain: 5 m × 5 m × 10 m
- Two equal layers meeting at z = 0
- Flow driven between the +Z and -Z faces (`boundaryFaces = [0,0,0,0,1,1]`)
- Both families use truncated power-law radii (1–10 m), so many fractures are large enough to cross the layer boundary

## Running the Example

```bash
python driver.py
```

To test a different mode, change `LAYER_CONFORMING` at the top of `driver.py`:

```python
LAYER_CONFORMING = 0  # disabled
LAYER_CONFORMING = 1  # perfect conforming
LAYER_CONFORMING = 2  # soft conforming (recommended)
```

## What to Expect

**Mode 0 (disabled)**  
Fractures from each family cross the layer interface freely. The DFN is well-connected but fractures violate the layer geometry. You should see fracture centers clustered in each layer but polygon vertices distributed throughout the full domain height in the output report center histograms.

**Mode 1 (perfect conforming)**  
Fracture polygons are hard-clipped at z = 0. The rejection rate ("Outside of Domain" in `rejections.dat`) will increase relative to mode 0 because some fractures are clipped to fewer than 3 vertices and discarded. Flow between layers depends entirely on fractures that naturally intersect near z = 0 before clipping. In thin-layer configurations or with high kappa (strongly oriented) families this can produce a disconnected network — if dfnFlow reports zero or very low effective permeability, this is likely why.

**Mode 2 (soft conforming, recommended)**  
Fracture polygons are clipped at z = ±0.2 m (2h = 2 × 0.1 m). The small overhang means fractures from layer 1 and layer 2 share a 0.4 m overlap zone near the interface, preserving intersections needed for flow. Rejection rate will be slightly lower than mode 1. Effective permeability should be comparable to mode 0 while still respecting layer geometry.

**Output report**  
The fracture center histograms in `dfnGen_output_report/family_*/` are the clearest visual check. In modes 1 and 2 the z-coordinate histograms should show hard cutoffs at the layer boundaries (with a small tail of ±2h in mode 2). In mode 0 the distributions will bleed across z = 0.

## Key Output Files

| File | Contents |
|------|----------|
| `dfnGen_output/DFN_output.txt` | Summary statistics including mode used |
| `dfnGen_output/rejections.dat` | Rejection counts by reason; monitor "Outside of Domain" |
| `dfnGen_output/families.dat` | Per-family parameters and acceptance statistics |
| `output_output_report.pdf` | Full visual report including center histograms and FRAM bar chart |
| `output/pboundary_*.ex` | PFLOTRAN boundary flux files for computing effective permeability |
