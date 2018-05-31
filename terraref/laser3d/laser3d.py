import subprocess
import numpy
import laspy
from plyfile import PlyData, PlyElement
from terrautils.spatial import scanalyzer_to_mac


def generate_las_from_ply(inp, out, side, metadata):
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

    # Attempt fix using math from terrautils.spatial.calculate_gps_bounds
    pco = metadata['sensor_variable_metadata']['point_cloud_origin_m'][side]
    scandist = float(metadata['sensor_variable_metadata']['scan_distance_mm'])/1000.0
    scan_dir = int(metadata['sensor_variable_metadata']['scan_direction'])
    # TODO: Should get camera box offsets from sensor fixed metadata instead
    if side == 'east':
        cambox = [2.070, 0.306, 1.135]
    else:
        cambox = [2.070, 2.726, 1.135]

    # Apply offset adjustment fix from terrautils.spatial.calculate_gps_bounds()
    fix_x = merged_x + cambox[0] + 0.082
    if scan_dir == 0:
        if side == 'east':
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 - 0.354
        else:
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 - 4.363
    else:
        if side == 'east':
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 + 0.4
        else:
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 - 4.23
    fix_z = merged_z + cambox[2]

    # Convert scanner coords to UTM and apply point cloud origin offset
    utm_x, utm_y = scanalyzer_to_mac(
            (fix_x * 0.001) + pco['x'],
            (fix_y * 0.001) + pco['y']/2.0
    )
    utm_z = (fix_z * 0.001)+ pco['z']

    # Create header and populate with scale and UTM-12 georeference offset
    w = laspy.base.Writer(out, 'w', laspy.header.Header())
    w.set_header_property("x_offset", numpy.floor(numpy.min(utm_x)))
    w.set_header_property("y_offset", numpy.floor(numpy.min(utm_y)))
    w.set_header_property("z_offset", numpy.floor(numpy.min(utm_z)))
    w.header.scale = [.000001, .000001, .000001]

    w.set_x(utm_x, True)
    w.set_y(utm_y, True)
    w.set_z(utm_z, True)
    w.header.update_min_max(True)
    w.close()


def generate_pdal_pipeline(filename, mode='max'):
    """
    Generate a temporary JSON file with PDAL pipeline for conversion to TIF
    """
    content = """{
        "pipeline": [
            "%s",
            {
                "filename":"%s",
                "output_type":"%s",
                "resolution": 0.1,
                "type": "writers.gdal",
                "gdalopts": "t_srs=epsg:32612"
            }
        ]
    }""" % (filename, filename.replace(".las", ".tif"), mode)

    with open("pdal_dtm.json", 'w') as dtm:
        dtm.write(content)


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

    # PKLAS2IMG
    #subprocess.call(['pklas2img -i '+inp+' -o '+out+' -comp '+mode+' -n z -nodata -1 -ot Float32'], shell=True)

    # PDAL
    #generate_pdal_pipeline(inp, mode)
    #subprocess.call(['pdal pipeline pdal_dtm.json'], shell=True)

    # LASTOOLS
    subprocess.call(['wine /lastools/bin/blast2dem.exe -force_precision -i '+inp+' -o '+out], shell=True)

def generate_slope_from_tif(inp, out):
    """
    Create a slope raster from a Digital Surface Map (e.g. canopy heightmap)
    :param inp: input GeoTIFF file
    :param out: output GeoTIFF file
    """
    pass
