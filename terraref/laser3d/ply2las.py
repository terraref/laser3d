import logging
import subprocess
import copy
import math
import laspy


def generate_las_from_pdal(pdal_base, in_east, tmp_east_las):
    """

    :param pdal_base: where the pdal is running
    :param in_east: local path to the ply file
    :param tmp_east_las: tmp path to the las file
    :return:
    """
    logging.getLogger(__name__).info("converting %s" % in_east)
    subprocess.call([pdal_base+'pdal translate ' + \
                     '--writers.las.dataformat_id="0" ' + \
                     '--writers.las.scale_x=".000001" ' + \
                     '--writers.las.scale_y=".0001" ' + \
                     '--writers.las.scale_z=".000001" ' + \
                     in_east + " " + tmp_east_las], shell=True)


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