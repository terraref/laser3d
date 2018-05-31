# laser3d science package

This repository contains utilities for scientific operations on 3D laser scanner data.

### laser3d.py

**generate_las_from_ply(inp, out, pco)**
Convert a list of PLY input files into a single merged LAS output.

**generate_tif_from_las(inp, out, mode='max')**
Convert an LAS file to a raster, using mode as the pixel aggregation rule.

**generate_slope_from_tif(inp, out)**
Convert a DSM to a slope raster.

### Authors:

* Maxwell Burnette, National Supercomputing Applications, Urbana, Il
