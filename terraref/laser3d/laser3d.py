import subprocess
import numpy
import laspy
from osgeo import gdal
from plyfile import PlyData, PlyElement
from terrautils.formats import create_geotiff
from terrautils.spatial import scanalyzer_to_mac


def generate_las_from_ply(inp, out):
    """
    :param inp: list of input PLY files or single file path
    :param out: output LAS file
    :param pco: point cloud origin from metadata e.g. md['sensor_variable_metadata']['point_cloud_origin_m']['east']
    """
    if not isinstance(inp, list):
        inp = [inp]

    scandist = float(md['sensor_variable_metadata']['scan_distance_mm'])/1000.0
    scan_dir = int(md['sensor_variable_metadata']['scan_direction'])
    pco = metadata['sensor_variable_metadata']['point_cloud_origin_m']['east']

    # Create concatenated list of vertices to generate one merged LAS file
    first = True
    for plyf in inp:
        if plyf.find("west") > -1:
            curr_side = "west"
            cambox = [2.070, 2.726, 1.135]
        else:
            curr_side = "east"
            cambox = [2.070, 0.306, 1.135]

        plydata = PlyData.read(plyf)
        merged_x = plydata['vertex']['x']
        merged_y = plydata['vertex']['y']
        merged_z = plydata['vertex']['z']

        fix_x = merged_x + cambox[0] + 0.082
        if scan_dir == 0:
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 + (
                -0.354 if curr_side == 'east' else -4.363)
            utm_x, utm_y = scanalyzer_to_mac(
                    (fix_x * 0.001) + pco['x'],
                    (fix_y * 0.001) + pco['y']/2.0 - 0.1
            )
        else:
            fix_y = merged_y + float(2.0*float(cambox[1])) - scandist/2.0 + (
                4.2 if curr_side == 'east' else -3.43)
            utm_x, utm_y = scanalyzer_to_mac(
                    (fix_x * 0.001) + pco['x'],
                    (fix_y * 0.001) + pco['y']/2.0 + 0.4
            )
        fix_z = merged_z + cambox[2]
        utm_z = (fix_z * 0.001)+ pco['z']

        if first:
            x_pts = fix_x
            y_pts = fix_y
            z_pts = utm_z

            min_x_utm = numpy.min(utm_x)
            min_y_utm = numpy.min(utm_y)
            max_x_utm = numpy.max(utm_x)
            max_y_utm = numpy.max(utm_y)

            first = False
        else:
            x_pts = numpy.concatenate([x_pts, fix_x])
            y_pts = numpy.concatenate([y_pts, fix_y])
            z_pts = numpy.concatenate([z_pts, utm_z])

            min_x_utm2 = numpy.min(utm_x)
            min_y_utm2 = numpy.min(utm_y)
            max_x_utm2 = numpy.max(utm_x)
            max_y_utm2 = numpy.max(utm_y)

            min_x_utm = min_x_utm if min_x_utm < min_x_utm2 else min_x_utm2
            min_y_utm = min_y_utm if min_y_utm < min_y_utm2 else min_y_utm2
            max_x_utm = max_x_utm if max_x_utm > max_x_utm2 else max_x_utm2
            max_y_utm = max_y_utm if max_y_utm > max_y_utm2 else max_y_utm2

    bounds = (min_y_utm, max_y_utm, min_x_utm, max_x_utm)

    if not os.path.exists(out.replace(".las", ".json")):
        # Create header and populate with scale and offset
        w = laspy.base.Writer(out, 'w', laspy.header.Header())
        w.header.offset = [numpy.floor(numpy.min(x_pts)),
                           numpy.floor(numpy.min(y_pts)),
                           numpy.floor(numpy.min(z_pts))]
        w.header.scale = [1, 1, .000001]

        w.set_x(y_pts, True)
        w.set_y(x_pts, True)
        w.set_z(z_pts, True)
        w.header.update_min_max(True)
        w.close()

    return bounds


def generate_pdal_pipeline(filename, output, mode='max'):
    """
    Generate a temporary JSON file with PDAL pipeline for conversion to TIF
    """
    content = """{
        "pipeline": [
            "%s",
            {
                "filename":"%s",
                "output_type":"%s",
                "resolution": 1,
                "type": "writers.gdal"
            }
        ]
    }""" % (filename, output, mode)
    # "gdalopts": "t_srs=epsg:32612"

    with open("pdal_dtm.json", 'w') as dtm:
        dtm.write(content)


def generate_tif_from_ply(inp, bounds, mode='max'):
    """
    Create a raster (e.g. Digital Surface Map) from LAS pointcloud.
    :param inp: input LAS file
    :param bounds: (min_y_utm, max_y_utm, min_x_utm, max_x_utm)
    :param mode: max | min | mean | median | sum (http://www.nongnu.org/pktools/html/md_pklas2img.html)

    generally:
        max = highest pixels in cell, usually canopy - equates to a DSM (Digital Surface Map)
        min = lowest pixel in a cell, usually soil - equates to DTM (Digital Terrain Map)
    """

    out_raw = inp.replace(".las", "_unref.tif")
    out_geo = inp.replace(".las", ".tif")
    generate_pdal_pipeline(inp, out_raw, mode)
    subprocess.call(['pdal pipeline pdal_dtm.json'], shell=True)

    ds = gdal.Open(out_raw)
    px = ds.GetRasterBand(1).ReadAsArray()
    #if scan_dir == 0:
    #   px = numpy.rot90(px, 2)
    #   x = numpy.fliplr(px)
    create_geotiff(px, bounds, out_geo, asfloat=True)
