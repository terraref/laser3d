import os
import subprocess
import pytest

# TODO: don't see a way to avoid requiring terrautils for this science package unless we duplicate code.
from terraref.terrautils.metadata import clean_metadata
from terraref.laser3d import generate_las_from_ply, generate_tif_from_las

dire = os.path.join(os.path.dirname(__file__), 'data/')


@pytest.fixture(scope='module')
def read_metadata():
    md_file = dire + 'metadata.json'
    with open(md_file, 'r') as mdf:
        md = clean_metadata(mdf, 'scanner3DTop')
    return md


# TODO dumb pointer to a static data file but could get file from
# alternate source

in_east = dire + 'east.ply'
in_west = dire + 'west.ply'

merge_las = dire + "merged.las"
eastout = dire + "merged_e.las"
westout = dire + "merged_w.las"

merged_tif = dire + "merged.tif"


def test_east_las(read_metadata):
    generate_las_from_ply(in_east, eastout, 'east', read_metadata)
    assert os.path.isfile(eastout)


def test_west_las(read_metadata):
    generate_las_from_ply(in_west, westout, 'west', read_metadata)
    assert os.path.isfile(westout)


def test_combine_file(read_metadata):
    generate_las_from_ply([in_east, in_west], merge_las, read_metadata)
    assert os.path.isfile(merge_las)


def test_combine_tif(read_metadata):
    generate_las_from_ply([in_east, in_west], merge_las, read_metadata)
    generate_tif_from_las(merge_las, merged_tif)
    assert os.path.isfile(merged_tif)

def test_remove_file():
    os.remove(eastout)
    os.remove(westout)
    os.remove(merge_las)


if __name__ == '__main__':
    subprocess.call(['python -m pytest test_ply2las.py -p no:cacheprovider'], shell=True)
