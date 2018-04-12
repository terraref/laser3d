import os
import subprocess
import pytest

from terraref.laser3d import generate_las_from_ply

dire = os.path.join(os.path.dirname(__file__), 'data/')


@pytest.fixture(scope='module')
def read_metadata():
    pcoe = {'y': 4.062, 'x': 171.652, 'z': 2.8050000000000006}
    pcow = {'y': 8.902000000000001, 'x': 171.652, 'z': 2.8050000000000006}
    return pcoe, pcow


# TODO dumb pointer to a static data file but could get file from
# alternate source

in_east = dire + 'neweast.ply'
in_west = dire + 'newwest.ply'
merge_las = dire + "merged.las"
eastout = dire + "merged_e.las"
westout = dire + "merged_w.las"


def test_east_las(read_metadata):
    generate_las_from_ply(in_east, eastout, read_metadata[0])
    assert os.path.isfile(eastout)


def test_west_las(read_metadata):
    generate_las_from_ply(in_west, westout, read_metadata[1])
    assert os.path.isfile(westout)


def test_combine_file(read_metadata):
    generate_las_from_ply([in_east, in_west], merge_las, read_metadata[0])
    assert os.path.isfile(merge_las)


def test_remove_file():
    os.remove(eastout)
    os.remove(westout)
    os.remove(merge_las)


if __name__ == '__main__':
    subprocess.call(['python -m pytest test_ply2las.py -p no:cacheprovider'], shell=True)
