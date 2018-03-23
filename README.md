# laser3d science package

This repository contains utilities for scientific operations on 3D laser scanner data.

### lasmerge.py

**merge_las_by_name(input_list, output)**
Merge a list of LAS files into one single file.

### ply2las.py

**generate_las_from_pdal(pdal_base, in_east, tmp_east_las)**
Use PDAL to convert a PLY file to LAS format.

**combine_east_west_las(pdal_base, tmp_east_las, tmp_west_las, merge_las)**
Use PDAL to merge two LAS files.

**geo_referencing_las(input_las_file, output_las_file, origin_coord)**

**geo_referencing_las_for_eachpoint_in_mac(input_las_file, output_las_file, origin_coord)**
