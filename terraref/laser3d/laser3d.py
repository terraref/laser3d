import logging
import subprocess
import copy
import math
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
    for plyf in inp:
        plydata = PlyData.read(plyf)
        for v in plydata['vertex']:
            pts.append(((int(v[0]*100), int(v[1]*100), int(v[2]*100), 0, 9, 0, 0, 0, 0),))

    # add geo-reference offset (UTM ZONE 12) to the las header
    h = laspy.header.Header()
    h.x_offset = pco['x']*1000
    h.y_offset = pco['y']*1000
    h.z_offset = pco['z']*1000

    # Create LAS file without georegistration
    f = laspy.file.File(out, h, mode='w')
    f.points = pts
    f.close()

    # translate each point to there MAC coordinate without any modify in header
    f = laspy.file.File(out, mode='r')
    h2 = copy.copy(f.header)
    h2.scale = [0.000001, 0.0001, 0.000001]
    f2 = laspy.file.File(out.replace('.las', '_geo.las'), h2, mode='w')
    f2.X = f.X + long(math.floor(pco['x']*100000))
    f2.Y = f.Y + long(math.floor(pco['y']*100000))
    f2.Z = f.Z + long(math.floor(pco['z']*100000))
    f.close()
    f2.close()


def combine_east_west_las(pdal_base, tmp_east_las, tmp_west_las, merge_las):
    logging.getLogger(__name__).info("merging %s + %s into %s" % (tmp_east_las, tmp_west_las, merge_las))
    subprocess.call([pdal_base+'pdal merge ' + \
                     tmp_east_las+' '+tmp_west_las+' '+merge_las], shell=True)


# This function add geo-reference offset(UTM ZONE 12) to the las header
def geo_referencing_las(input_las_file, output_las_file, origin_coord):
    #open las file
    inFile = laspy.file.File(input_las_file, mode='r')

    #get input header
    input_header = inFile.header

    # create output header
    output_header = copy.copy(input_header)

    output_header.x_offset = origin_coord['x']*1000
    output_header.y_offset = origin_coord['y']*1000
    output_header.z_offset = origin_coord['z']*1000

    # save as new las file
    output_file = laspy.file.File(output_las_file, mode='w', header=output_header)
    output_file.points = inFile.points
    output_file.close()

    return

# This function translate each point to there MAC coordinate without any modify in header
def geo_referencing_las_for_eachpoint_in_mac(input_las_file, output_las_file, origin_coord):

    # open las file
    inFile = laspy.file.File(input_las_file, mode='r')

    # output handle
    new_header = copy.copy(inFile.header)
    new_header.scale = [0.01,0.01,0.01]
    output_file = laspy.file.File(output_las_file, mode='w', header=new_header)

    output_file.X = inFile.X + long(math.floor(origin_coord['x']*100000))
    output_file.Y = inFile.Y + long(math.floor(origin_coord['y']*100000))
    output_file.Z = inFile.Z + long(math.floor(origin_coord['z']*100000))

    output_file.close()

def merge_las_by_name(input_list, output):
    """
    input a list of las files location, the function will generate a merged las file to output directory
    :param input_list: list of location of input files
    :param output: string of output file location
    :return:no return needed
    """

    basedire = os.path.join(os.path.dirname(__file__),"LAStools","bin","lasmerge")
    inputform = ["-i "+s for s in input_list]
    inputform = " ".join(inputform)
    outputform = "-o " + output
    sp_input = [basedire+" "+ inputform +" "+outputform]
    FNULL = open(os.devnull, 'w')
    subprocess.call(["make clean"],shell=True, stdout=FNULL,stderr=subprocess.STDOUT)
    subprocess.call(["make"],shell=True,stdout=FNULL, stderr=subprocess.STDOUT)
    subprocess.call(sp_input,shell=True,stdout=FNULL, stderr=subprocess.STDOUT)