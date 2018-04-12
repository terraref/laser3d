# laser3d science package

This repository contains utilities for scientific operations on 3D laser scanner data.

### laser3d.py

**generate_las_from_ply(inp, out, pco)**
Convert a list of PLY input files into a single merged LAS output.

**generate_tif_from_las(inp, out, mode='max')**
Convert an LAS file to a raster, using mode as the pixel aggregation rule.

**generate_slope_from_tif(inp, out)**
Convert a DSM to a slope raster.

## Installing dependencies

This package has several dependencies. 

Conversion from PLY to LAS requires plyfile and laspy python libraries.
```
pip install laspy plyfile
```
These will be automatically installed if you use:
```
pip install terraref-laser3d
```

Conversion from LAS to GeoTIFF requires the external pktools with libLAS support.
```
# boost
wget https://dl.bintray.com/boostorg/release/1.66.0/source/boost_1_66_0.tar.bz2 && tar xvjf boost_1_66_0.tar.bz2
export BOOST_LIBRARYDIR=/boost_1_66_0/libs

# libLAS
apt-get update && apt-get install -y cmake libboost-dev libboost-all-dev
wget http://download.osgeo.org/liblas/libLAS-1.8.1.tar.bz2 && tar xvjf libLAS-1.8.1.tar.bz2
cd libLAS-1.8.1 && mkdir makefiles && cd makefiles
/sbin/ldconfig

# pktools
apt-get install -y g++ libgdal-dev libgsl0-dev libarmadillo-dev liblas-dev python-liblas liblas-c-dev
wget http://download.savannah.gnu.org/releases/pktools/pktools-latest.tar.gz && tar xvzf pktools-latest.tar.gz
cd PKTOOLS-2.6.7.3 && mkdir build && cd build
cmake -DBUILD_WITH_LIBLAS=ON .. && make && make install
```
