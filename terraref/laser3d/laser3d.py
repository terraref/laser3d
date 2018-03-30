import subprocess
import math
import numpy
import laspy
from plyfile import PlyData, PlyElement


def generate_las_from_ply(inp, out, pco):
    """
    :param inp: list of input PLY files or single file path
    :param out: output LAS file
    :param pco: point cloud origin from metadata e.g. md['sensor_variable_metadata']['point_cloud_origin_m']['east']
    """
    if not isinstance(inp, list):
        inp = [inp]

    # Create concatenated list of vertices to generate one merged LAS file
    first = True
    for plyf in inp:
        plydata = PlyData.read(plyf)
        merged_x = plydata['vertex']['x'] if first else numpy.concatenate([merged_x, plydata['vertex']['x']])
        merged_y = plydata['vertex']['y'] if first else numpy.concatenate([merged_y, plydata['vertex']['y']])
        merged_z = plydata['vertex']['z'] if first else numpy.concatenate([merged_z, plydata['vertex']['z']])
        first = False

    # Create header and populate with scale and UTM-12 georeference offset
    w = laspy.base.Writer(out, 'w', laspy.header.Header())
    w.header.scale = [0.01, 0.01, 0.01]
    w.set_header_property("x_offset", pco['x']*1000)
    w.set_header_property("y_offset", pco['y']*1000)
    w.set_header_property("z_offset", pco['z']*1000)

    # Add actual points from PLY files and update statistics to LAS file
    w.set_x(merged_x, True)
    w.set_y(merged_y, True)
    w.set_z(merged_z, True)
    w.header.update_min_max()
    w.close()

    # Skip creation of f2 for now
    return

    # TODO: this replaces geo_referencing_las_for_eachpoint_in mac - is it still necessary?
    f = laspy.file.File(out, mode='r')
    f2 = laspy.file.File(out.replace('.las', '_geo.las'), f.header, mode='w')
    f2.X = f.X + long(math.floor(pco['x']*100000))
    f2.Y = f.Y + long(math.floor(pco['y']*100000))
    f2.Z = f.Z + long(math.floor(pco['z']*100000))
    f.close()
    f2.close()


def generate_tif_from_las(inp, out, mode='max'):
    """
    Create a raster (e.g. Digital Surface Map) from LAS pointcloud.
    :param inp: input LAS file
    :param out: output GeoTIFF file
    :param mode: max | min | mean | median | sum (http://www.nongnu.org/pktools/html/md_pklas2img.html)

    generally:
        max = highest pixels in cell, usually canopy - equates to a DSM (Digital Surface Map)
        min = lowest pixel in a cell, usually soil - equates to DTM (Digital Terrain Map)
    """
    subprocess.call(['pklas2img -i '+inp+' -o '+out+' -comp '+mode+' -n z -nodata -1 -ot Float32'], shell=True)


def generate_slope_from_tif(inp, out):
    """
    Create a slope raster from a Digital Surface Map (e.g. canopy heightmap)
    :param inp: input GeoTIFF file
    :param out: output GeoTIFF file
    """
    pass
