import os
import logging
import subprocess
import pytest

from terrautils.metadata import get_terraref_metadata, clean_metadata
from terrautils.extractors import load_json_file
from terraref.laser3d import *


dire = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='module')
def read_metadata():
    all_dsmd = load_json_file(dire + '/metadata.json')
    cleanmetadata = clean_metadata(all_dsmd, "scanner3DTop")
    terra_md = get_terraref_metadata(cleanmetadata, 'scanner3DTop')
    return terra_md
# TODO dumb pointer to a static data file but could get file from
# alternate source

in_east = '/data/' + 'neweast.ply'
in_west = '/data/' + 'newwest.ply'

pdal_base = "docker run -v %s:/data pdal/pdal:1.5 " % dire
tmp_east_las = "/data/east_temp.las"
tmp_west_las = "/data/west_temp.las"
merge_las = "/data/merged.las"
convert_las = dire+"/converted.las"
convert_pt_las = dire+"/converted_pts.las"


def test_east_las():
    generate_las_from_pdal(pdal_base, in_east, tmp_east_las)
    assert os.path.isfile(dire + '/east_temp.las')


def test_west_las():
    generate_las_from_pdal(pdal_base, in_west, tmp_west_las)
    assert os.path.isfile(dire + '/west_temp.las')


def test_combine_file():
    combine_east_west_las(pdal_base, tmp_east_las, tmp_west_las, merge_las)
    assert os.path.isfile(dire + '/merged.las')

logging.getLogger(__name__).info("converting LAS coordinates")


def test_scanner_func(read_metadata):
    point_cloud_origin = read_metadata['sensor_variable_metadata']['point_cloud_origin_m']['east']
    geo_referencing_las(dire + '/merged.las', convert_las, point_cloud_origin)
    geo_referencing_las_for_eachpoint_in_mac(convert_las, convert_pt_las, point_cloud_origin)
    assert os.path.isfile(convert_las)
    assert os.path.isfile(convert_pt_las)


def test_remove_file():
    os.remove(dire + '/east_temp.las')
    os.remove(dire + '/west_temp.las')
    os.remove(dire + '/merged.las')
    os.remove(convert_las)
    os.remove(convert_pt_las)
    assert os.path.isfile(dire + '/east_temp.las') == False
#

if __name__ == '__main__':
    subprocess.call(['python -m pytest test_ply2las.py -p no:cacheprovider'], shell=True)
