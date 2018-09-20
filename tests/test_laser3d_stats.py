import os
import subprocess
import pytest
from terraref.laser3d import tif_sample, tif_mean, tif_var, fit_rleafangle_tiff

dire = os.path.join(os.path.dirname(__file__), 'data/')


@pytest.fixture(scope='module')
def read_metadata():
    return dire + 'scanner3DTop_L2_ua-mac_2018-07-08__04-51-55-343_heightmap.tif'


def test_geotiffstats(read_metadata):
    assert len(tif_sample(read_metadata)) == 1000
    assert tif_mean(read_metadata) > 2.6
    assert tif_var(read_metadata) < 0.184


def test_fit_leafangle_tiff(read_metadata):
    df = fit_rleafangle_tiff(read_metadata)
    assert df['mean'][1] < 90.


if __name__ == '__main__':
    subprocess.call(['python -m pytest test_laser3d_stats.py -p no:cacheprovider'], shell=True)
