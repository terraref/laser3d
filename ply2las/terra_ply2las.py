#!/usr/bin/env python

import os
import logging
import shutil
import subprocess
import copy
import math
import laspy

from pyclowder.utils import CheckMessage
from pyclowder.files import upload_to_dataset
from pyclowder.datasets import upload_metadata
from terrautils.metadata import get_terraref_metadata
from terrautils.extractors import TerrarefExtractor, is_latest_file, \
    build_dataset_hierarchy, build_metadata, load_json_file
from terrautils.spatial import scanalyzer_to_mac


def add_local_arguments(parser):
    # add any additional arguments to parser
    parser.add_argument('--dockerpdal', dest="pdal_docker", type=bool, nargs='?', default=False,
                        help="whether PDAL should be run inside a docker container")

class Ply2LasConverter(TerrarefExtractor):
    def __init__(self):
        super(Ply2LasConverter, self).__init__()

        add_local_arguments(self.parser)

        # parse command line and load default logging configuration
        self.setup(sensor="laser3d_mergedlas")

        # assign other arguments
        self.pdal_docker = self.args.pdal_docker

    # Check whether dataset already has metadata
    def check_message(self, connector, host, secret_key, resource, parameters):
        if "rulechecked" in parameters and parameters["rulechecked"]:
            return CheckMessage.download

        if not is_latest_file(resource):
            return CheckMessage.ignore

        # Check if we have 2 PLY files, but not an LAS file already
        east_ply = None
        west_ply = None
        for p in resource['files']:
            if p['filename'].endswith(".ply"):
                if p['filename'].find("east") > -1:
                    east_ply = p['filepath']
                elif p['filename'].find("west") > -1:
                    west_ply = p['filepath']

        if east_ply and west_ply:
            timestamp = resource['dataset_info']['name'].split(" - ")[1]
            out_las = self.sensors.get_sensor_path(timestamp)
            if os.path.exists(out_las) and not self.overwrite:
                logging.getLogger(__name__).info("output LAS file already exists; skipping %s" % resource['id'])
            else:
                return CheckMessage.download

        return CheckMessage.ignore

    def process_message(self, connector, host, secret_key, resource, parameters):
        self.start_message()
        uploaded_file_ids = []

        east_ply = None
        west_ply = None
        for p in resource['local_paths']:
            if p.endswith(".ply"):
                if p.find("east") > -1:
                    east_ply = p
                elif p.find("west") > -1:
                    west_ply = p
            elif p.endswith('_dataset_metadata.json'):
                all_dsmd = load_json_file(p)
                terra_md = get_terraref_metadata(all_dsmd)

        # Create output in same directory as input, but check name
        timestamp = resource['dataset_info']['name'].split(" - ")[1]
        out_las = self.sensors.create_sensor_path(timestamp)

        if not os.path.exists(out_las) or self.overwrite:
            if self.args.pdal_docker:
                pdal_base = "docker run -v /home/extractor:/data pdal/pdal:1.5 "
                in_east = east_ply.replace("/home/extractor/sites", "/data/sites")
                in_west = west_ply.replace("/home/extractor/sites", "/data/sites")
                tmp_east_las = "/data/east_temp.las"
                tmp_west_las = "/data/west_temp.las"
                merge_las = "/data/merged.las"
                convert_las = "/data/converted.las"
                convert_pt_las = "/data/converted_pts.las"
            else:
                pdal_base = ""
                in_east = east_ply
                in_west = west_ply
                tmp_east_las = "east_temp.las"
                tmp_west_las = "west_temp.las"
                merge_las = "/home/extractor/merged.las"
                convert_las = "/home/extractor/converted.las"
                convert_pt_las = "/home/extractor/converted_pts.las"

            logging.getLogger(__name__).info("converting %s" % east_ply)
            subprocess.call([pdal_base+'pdal translate ' + \
                             '--writers.las.dataformat_id="0" ' + \
                             '--writers.las.scale_x=".000001" ' + \
                             '--writers.las.scale_y=".0001" ' + \
                             '--writers.las.scale_z=".000001" ' + \
                             in_east + " " + tmp_east_las], shell=True)

            logging.getLogger(__name__).info("converting %s" % west_ply)
            subprocess.call([pdal_base+'pdal translate ' + \
                             '--writers.las.dataformat_id="0" ' + \
                             '--writers.las.scale_x=".000001" ' + \
                             '--writers.las.scale_y=".0001" ' + \
                             '--writers.las.scale_z=".000001" ' + \
                             in_west + " " + tmp_west_las], shell=True)

            logging.getLogger(__name__).info("merging %s + %s into %s" % (tmp_east_las, tmp_west_las, merge_las))
            subprocess.call([pdal_base+'pdal merge ' + \
                             tmp_east_las+' '+tmp_west_las+' '+merge_las], shell=True)

            logging.getLogger(__name__).info("converting LAS coordinates")
            # TODO: Should this use east or west if merged?
            point_cloud_origin = terra_md['sensor_variable_metadata']['point_cloud_origin_m']['east']
            # TODO: Leave as gantry coordinate system, or convert to MAC?
            #adj_x, adj_y = scanalyzer_to_mac(point_cloud_origin['x'], point_cloud_origin['y'])
            #adj_pco = (adj_x, adj_y, point_cloud_origin['z'])
            self.geo_referencing_las(merge_las, convert_las, point_cloud_origin)
            self.geo_referencing_las_for_eachpoint_in_mac(convert_las, convert_pt_las, point_cloud_origin)

            if os.path.exists(convert_pt_las):
                shutil.move(convert_pt_las, out_las)
                logging.getLogger(__name__).info("...created %s" % out_las)
                if os.path.isfile(out_las) and out_las not in resource["local_paths"]:
                    target_dsid = build_dataset_hierarchy(host, secret_key, self.clowder_user, self.clowder_pass, self.clowderspace,
                                                          self.sensors.get_display_name(),
                                                          timestamp[:4], timestamp[5:7],timestamp[8:10],
                                                          leaf_ds_name=self.sensors.get_display_name()+' - '+timestamp)

                    # Send LAS output to Clowder source dataset
                    fileid = upload_to_dataset(connector, host, secret_key, target_dsid, out_las)
                    uploaded_file_ids.append(fileid)

            self.created += 1
            self.bytes += os.path.getsize(out_las)

            if os.path.exists(tmp_east_las):
                os.remove(tmp_east_las)
            if os.path.exists(tmp_west_las):
                os.remove(tmp_west_las)
            if os.path.exists(merge_las):
                os.remove(merge_las)
            if os.path.exists(convert_las):
                os.remove(convert_las)

            # Tell Clowder this is completed so subsequent file updates don't daisy-chain
            metadata = build_metadata(host, self.extractor_info, resource['id'], {
                "files_created": [host + ("" if host.endswith("/") else "/") + "files/" + fileid]}, 'dataset')
            upload_metadata(connector, host, secret_key, resource['id'], metadata)

            # Upload original Lemnatec metadata to new Level_1 dataset
            terra_md['raw_data_source'] = host + ("" if host.endswith("/") else "/") + "datasets/" + resource['id']
            lemna_md = build_metadata(host, self.extractor_info, target_dsid, terra_md, 'dataset')
            upload_metadata(connector, host, secret_key, target_dsid, lemna_md)

            self.end_message()

    # This function add geo-reference offset(UTM ZONE 12) to the las header
    def geo_referencing_las(self, input_las_file, output_las_file, origin_coord):

        # open las file
        inFile = laspy.file.File(input_las_file, mode='r')

        # get input header
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
    def geo_referencing_las_for_eachpoint_in_mac(self, input_las_file, output_las_file, origin_coord):

        # open las file
        inFile = laspy.file.File(input_las_file, mode='r')

        # output handle
        new_header = copy.copy(inFile.header)
        src_header = inFile.header
        new_header.scale = [0.01,0.01,0.01]
        output_file = laspy.file.File(output_las_file, mode='w', header=new_header)

        #output_file.points = inFile.points
        # do the translating to each point
        output_file.X = inFile.X + long(math.floor(origin_coord['x']*100000))
        output_file.Y = inFile.Y + long(math.floor(origin_coord['y']*100000))
        output_file.Z = inFile.Z + long(math.floor(origin_coord['z']*100000))

        output_file.close()

        return

if __name__ == "__main__":
    extractor = Ply2LasConverter()
    extractor.start()
