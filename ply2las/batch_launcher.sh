#!/bin/bash
# this script is called to invoke one instance of ply2las extractor.

# Load necessary modules
module purge
module load python/2.7.10 pythonlibs/2.7.10 GCC proj4 pdal

# Activate python virtualenv
source /projects/arpae/terraref/shared/extractors/pyenv/bin/activate

# Run extractor script
python /projects/arpae/terraref/shared/extractors/extractors-3dscanner/ply2las/terra_ply2las.py
