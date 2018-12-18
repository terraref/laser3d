import subprocess
import numpy
import os
import laspy
from osgeo import gdal
from plyfile import PlyData, PlyElement
import matplotlib.pyplot as plt
from rpy2.robjects import r, pandas2ri, numpy2ri

from terrautils.formats import create_geotiff
from terrautils.spatial import scanalyzer_to_mac


def ply_to_array(inp, md, utm):
    """Read PLY files into a numpy matrix.

    :param inp: list of input PLY files or single file path
    :param md: metadata for the PLY files
    :param utm: True to return coordinates to UTM, False to return gantry fixed coordinates
    :return: tuple of (x_points, y_points, z_points, utm_bounds)
    """
    if not isinstance(inp, list):
        inp = [inp]

    scandist = float(md['sensor_variable_metadata']['scan_distance_mm'])/1000.0
    scan_dir = int(md['sensor_variable_metadata']['scan_direction'])
    pco = md['sensor_variable_metadata']['point_cloud_origin_m']['east']

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

        # Attempt fix using math from terrautils.spatial.calculate_gps_bounds
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

        # Create matrix of fixed gantry coords for TIF, but min/max of UTM coords for georeferencing
        if first:
            if utm:
                x_pts = utm_x
                y_pts = utm_y
            else:
                x_pts = fix_x
                y_pts = fix_y
            z_pts = utm_z

            min_x_utm = numpy.min(utm_x)
            min_y_utm = numpy.min(utm_y)
            max_x_utm = numpy.max(utm_x)
            max_y_utm = numpy.max(utm_y)

            first = False
        else:
            if utm:
                x_pts = numpy.concatenate([x_pts, utm_x])
                y_pts = numpy.concatenate([y_pts, utm_y])
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

    return (x_pts, y_pts, z_pts, bounds)

def generate_las_from_ply(inp, out, md, utm=True):
    """Read PLY file to array and write that array to an LAS file.

    :param inp: list of input PLY files or single file path
    :param out: output LAS file
    :param md: metadata for the PLY files
    :param utm: True to return coordinates to UTM, False to return gantry fixed coordinates
    """
    (x_pts, y_pts, z_pts, bounds) = ply_to_array(inp, md, utm)

    # Create header and populate with scale and offset
    w = laspy.base.Writer(out, 'w', laspy.header.Header())
    w.header.offset = [numpy.floor(numpy.min(y_pts)),
                       numpy.floor(numpy.min(x_pts)),
                       numpy.floor(numpy.min(z_pts))]
    if utm:
        w.header.scale = [.000001, .000001, .000001]
    else:
        w.header.scale = [1, 1, .000001]

    w.set_x(y_pts, True)
    w.set_y(x_pts, True)
    w.set_z(z_pts, True)
    w.set_header_property("x_max", numpy.max(y_pts))
    w.set_header_property("x_min", numpy.min(y_pts))
    w.set_header_property("y_max", numpy.max(x_pts))
    w.set_header_property("y_min", numpy.min(x_pts))
    w.set_header_property("z_max", numpy.max(z_pts))
    w.set_header_property("z_min", numpy.min(z_pts))
    w.close()

    return bounds

def generate_tif_from_ply(inp, out, md, mode='max'):
    """
    Create a raster (e.g. Digital Surface Map) from LAS pointcloud.
    :param inp: input LAS file
    :param out: output TIF file
    :param md: metadata for the PLY files
    :param mode: max | min | mean | idx | count | stdev (https://pdal.io/stages/writers.gdal.html)
    """

    pdal_dtm = out.replace(".tif", "_dtm.json")
    las_raw = out.replace(".tif", "_temp.las")
    tif_raw = out.replace(".tif", "unreferenced.tif")

    bounds = generate_las_from_ply(inp, las_raw, md, False)

    if not os.path.exists(tif_raw):
        # Generate a temporary JSON file with PDAL pipeline for conversion to TIF and execute it
        with open(pdal_dtm, 'w') as dtm:
            dtm.write("""{
            "pipeline": [
                "%s",
                {
                    "filename":"%s",
                    "output_type":"%s",
                    "resolution": 1,
                    "type": "writers.gdal"
                }
            ]
        }""" % (las_raw, tif_raw, mode))
        # "gdalopts": "t_srs=epsg:32612"

        cmd = 'pdal pipeline %s' % pdal_dtm
        subprocess.call([cmd], shell=True)

    os.remove(las_raw)

    # Georeference the unreferenced TIF file according to PLY UTM bounds
    ds = gdal.Open(tif_raw)
    px = ds.GetRasterBand(1).ReadAsArray()
    #if scan_dir == 0:
    #   px = numpy.rot90(px, 2)
    #   x = numpy.fliplr(px)
    create_geotiff(px, bounds, out, asfloat=True)

    os.remove(tif_raw)

def load_tif_vector(heightmap_tif):
    """Load heightmap geotiff into a vector for other methods."""

    f = gdal.Open(heightmap_tif)
    vector = numpy.array(f.GetRasterBand(1).ReadAsArray())
    vector[vector == -9999.] = numpy.nan
    return vector

def tif_sample(geotiff, sample_num=1000, vector=None):
    """Return random sampling of heightmap values.

        vector: Use already-loaded vector instead of reloading."""

    if not vector:
        vector = load_tif_vector(geotiff)
    return numpy.random.choice(vector[~numpy.isnan(vector)], sample_num)

def tif_mean(geotiff, vector=None):
    """Get average of geotiff values.

        vector: Use already-loaded vector instead of reloading."""

    if not vector:
        vector = load_tif_vector(geotiff)
    return numpy.nanmean(vector)

def tif_var(geotiff, vector=None):
    """Get variance of geotiff values.

        vector: Use already-loaded vector instead of reloading."""

    if not vector:
        vector = load_tif_vector(geotiff)
    return numpy.nanvar(vector)

def tif_hist(geotiff, save=False, vector=None):
    """Get histogram of geotiff values.

        save: False, or a path to .png file.
        vector: Use already-loaded vector instead of reloading.
    """
    if not vector:
        vector = load_tif_vector(geotiff)
    newv = numpy.concatenate(vector, axis=0)

    plt.hist(newv[~numpy.isnan(newv)], 50, normed=1, facecolor='green', alpha=0.75)
    plt.xlabel('Geotiff value')
    plt.ylabel('Probability')
    plt.title('Histogram of Geotiff')
    if save:
        plt.savefig(save)
        plt.close()
    else:
        plt.show()

def tif_fit_rleafangle(geotiff):
    """Use R to fit leaf angle."""
    f = gdal.Open(geotiff)
    vector = numpy.concatenate(numpy.array(f.GetRasterBand(1).ReadAsArray()), axis=0)
    vector[vector == -9999.] = numpy.nan
    newvector = vector[~numpy.isnan(vector)]
    rstring = """
        function(angles){
          n <- length(angles)
          betapara <- RLeafAngle::computeBeta(angles)
          result <- data.frame(rbind(
            c(trait    = 'leaf_angle_twoparbeta',
              beta1    =  betapara[1],
              beta2    = betapara[2],
              mean     = betapara[1]/(betapara[1]+betapara[2]),
              variance = betapara[1]*betapara[2]/(betapara[1]+betapara[2])/(betapara[1]+betapara[2])/(betapara[1]+betapara[2]+1),
              n        = n)))
          return(result)
        }
        """
    numpy2ri.activate()
    rfunc = r(rstring)
    r_df = rfunc(newvector)
    newdf = pandas2ri.ri2py(r_df)
    return newdf

def tif_fit_pyleafangle(geotiff):
    """Use Python to fit leaf angle."""
    f = gdal.Open(geotiff)
    vector = numpy.concatenate(numpy.array(f.GetRasterBand(1).ReadAsArray()), axis=0)
    vector[vector == -9999.] = numpy.nan
    newvector = vector[~numpy.isnan(vector)]

    xbar = numpy.mean(newvector)
    xvar = numpy.var(newvector)
    alpha = (((1 - xbar) / xvar - 1) / xbar) * (xbar ^ 2)
    beta = alpha * (1 / xbar - 1)

    return ('leaf_angle_twoparbeta', alpha, beta, xbar, xvar)
