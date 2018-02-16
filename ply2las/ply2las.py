'''
Created on Oct 3, 2017

@author: zli
'''
import os, argparse, sys, json, math
import numpy as np
import laspy
import copy

# Scanalyzer -> MAC formular
# Mx = ax + bx * Gx + cx * Gy
# My = ay + by * Gx + cy * Gy
ay = 3659974.971; by = 1.0002; cy = 0.0078
ax = 409012.2032; bx = 0.009; cx = -0.9986

def main():
    
    las_path = '/media/zli/data/Terra/sample_files/scanner3dTop/2017-07-03/2017-07-03__01-11-05-770/scanner3DTop_L1_ua-mac_2017-07-03__01-11-05-770_merged.las'
    out_path = '/media/zli/data/Terra/sample_files/scanner3dTop/2017-07-03/2017-07-03__01-11-05-770/fixed_header_mac.las'
    file_id = 0
    json_path = '/media/zli/data/Terra/sample_files/scanner3dTop/2017-07-03/2017-07-03__01-11-05-770/23154db0-9771-4955-b4e4-70903278486e_metadata.json'
    
    geo_referencing_las_for_eachpoint_in_mac(las_path, out_path, file_id, json_path)
    
    return


# This function add geo-reference offset(UTM ZONE 12) to the las header
def geo_referencing_las(input_las_file, output_las_file, file_id, json_file):
    
    # open las file
    inFile = laspy.file.File(input_las_file, mode='r')
    
    # get input header
    input_header = inFile.header
    
    # create output header
    output_header = copy.copy(input_header)
    origin_coord = get_origin_utm_coordinate(json_file, True)
    
    output_header.x_offset = origin_coord[0]*1000
    output_header.y_offset = origin_coord[1]*1000
    output_header.z_offset = origin_coord[2]*1000
    
    # save as new las file
    output_file = laspy.file.File(output_las_file, mode='w', header=output_header)
    output_file.points = inFile.points
    output_file.close()
    
    return

# This function translate each point to there MAC coordinate without any modify in header
def geo_referencing_las_for_eachpoint_in_mac(input_las_file, output_las_file, file_id, json_file):
    
    # open las file
    inFile = laspy.file.File(input_las_file, mode='r')
    
    # output handle
    new_header = copy.copy(inFile.header)
    src_header = inFile.header
    new_header.scale = [0.01,0.01,0.01]
    output_file = laspy.file.File(output_las_file, mode='w', header=new_header)
    
    origin_coord = get_origin_utm_coordinate(json_file, True)
    
    #output_file.points = inFile.points
    # do the translating to each point
    output_file.X = inFile.X + long(math.floor(origin_coord[0]*100000))
    output_file.Y = inFile.Y + long(math.floor(origin_coord[1]*100000))
    output_file.Z = inFile.Z + long(math.floor(origin_coord[2]*100000))
    
    
    output_file.close()
    
    return

def get_origin_utm_coordinate(json_file, use_mac=False):
    
    metadata = lower_keys(load_json(json_file))
    
    scan_start_position = get_position(metadata) # scan_start_position: gantry position + camera position
    
    # all the offset has been declare @: https://github.com/terraref/reference-data/issues/44#issuecomment-299336814
    x = scan_start_position[0] + 0.082 # x direction +82mm to the north
    z = (scan_start_position[2] + 0.3) - 3.445 # z direction +3.445m, +0.3 for gantry z 0 is 0.3 meters higher than the ground
    
    # y is only relate to the origin offset
    if scan_start_position[1]==0:
        y = 3.45  # positive scan, +3.45m y offset
    else:
        y = 25.771 # negative scan, +25.771m y offset
    
    if use_mac:
        Mx, My = scanalyzer2MAC(x, y)
        return [Mx, My, z]
    else:
        return [x, y, z]

def scanalyzer2MAC(Gx, Gy):
    
    Mx = ax + bx * Gx + cx * Gy
    My = ay + by * Gx + cy * Gy
    
    return Mx, My

def load_json(meta_path):
    try:
        with open(meta_path, 'r') as fin:
            return json.load(fin)
    except Exception as ex:
        fail('Corrupt metadata file, ' + str(ex))
    
    
def lower_keys(in_dict):
    if type(in_dict) is dict:
        out_dict = {}
        for key, item in in_dict.items():
            out_dict[key.lower()] = lower_keys(item)
        return out_dict
    elif type(in_dict) is list:
        return [lower_keys(obj) for obj in in_dict]
    else:
        return in_dict

def get_position(metadata):
    try:
        gantry_meta = metadata['lemnatec_measurement_metadata']['gantry_system_variable_metadata']
        gantry_x = gantry_meta["position x [m]"]
        gantry_y = gantry_meta["position y [m]"]
        gantry_z = gantry_meta["position z [m]"]
        
        sensor_fix_meta = metadata['lemnatec_measurement_metadata']['sensor_fixed_metadata']
        camera_x = sensor_fix_meta['scanner west location in camera box x [m]']
        camera_z = sensor_fix_meta['scanner west location in camera box z [m]']
        

    except KeyError as err:
        fail('Metadata file missing key: ' + err.args[0])
        return(0, 0, 0)

    try:
        x = float(gantry_x) + float(camera_x)
        y = float(gantry_y)
        z = float(gantry_z) + float(camera_z)
    except ValueError as err:
        fail('Corrupt positions, ' + err.args[0])
    return (x, y, z)

def fail(reason):
    print >> sys.stderr, reason

if __name__ == "__main__":

    main()
