import os
import sys
import json
import csv
import logging
import pytest

#from terrautils.metadata import clean_metadata, get_terraref_metadata
from ply2las.ply2las import *


@pytest.fixture(scope='module')
def read_metadata():
    fname = os.path.join(os.path.dirname(__file__), 'data/metadata.json')
    with open(fname) as f:
        metadata = json.load(f)
    return metadata


# # TODO dumb pointer to a static data file but could get file from
# # alternate source
# @pytest.fixture(scope='module')
# def binfile():
#     return os.path.join(os.path.dirname(__file__), 'data/binfile.bin')
#
#
# @pytest.mark.parametrize("metadata,side", [
#     (read_metadata(), 'left'),
#     (read_metadata(), 'right'),
# ])
# def test_get_image_shape(metadata, side):
#     dims = get_image_shape(metadata, side)
#     assert len(dims) == 2
#     width, height = dims
#
#     assert isinstance(width, int)
#     assert isinstance(height, int)
#     assert width > 0
#     assert height > 0
#
#
# def test_process_raw(binfile):
#     dims = get_image_shape(read_metadata(), 'left')
#     im = process_raw(dims, binfile)
#     assert im.any
#     assert im.shape[0] == dims[0]
#     assert im.shape[1] == dims[1]
#     assert im.shape[2] == 3   # r,g,b
#
#
# def test_process_raw_with_save(binfile, tmpdir):
#     dims = get_image_shape(read_metadata(), 'left')
#     outfile = str(tmpdir.mkdir('save_test').join('output.jpeg'))
#     im = process_raw(dims, binfile, outfile)
#     assert os.path.exists(outfile)
#
#
# def test_get_traits_table():
#     fields, traits = get_traits_table()
#     assert len(fields) == len(traits.keys())
#     for f in fields:
#         assert f in traits.keys()
#
# def test_generate_traits_list():
#     fields, traits = get_traits_table()
#     trait_list = generate_traits_list(traits)
#     assert len(fields) == len(trait_list)
#
# def test_generate_cc_csv(tmpdir):
#     """check the generation of the CSV file used update betydb
#
#     Method:
#       1) generate the traits table
#       2) update the 'species' field
#       3) write to CSV
#       4) read CSV with python csv module
#       5) assert species is set to test value
#     """
#
#     fname = str(tmpdir.mkdir('csv_test').join('out.csv'))
#
#     fields, traits = get_traits_table()
#     traits['species'] = 'test'
#     trait_list = generate_traits_list(traits)
#     retname = generate_cc_csv(fname, fields, trait_list)
#     assert fname == retname
#
#     # ensure the CSV is parsable the standard module
#     with open(retname) as f:
#         results = csv.reader(f)
#         headers = results.next()
#         values = results.next()
#
#     idx = headers.index('species')
#     assert idx != -1
#     assert values[idx] == 'test'
#
# def test_calculate_canopycover():
#     pass
