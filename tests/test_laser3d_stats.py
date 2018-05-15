import os
import subprocess
import pytest
from terraref.laser3d import GeotiffStats, fit_leafangle_r

dire = os.path.join(os.path.dirname(__file__), 'data/')


@pytest.fixture(scope='module')
def read_metadata():
    return dire + 'ir_geotiff_L1_ua-mac_2018-02-28__10-55-35-774.tif'


def test_geotiffstats(read_metadata):
    geostatsObject = GeotiffStats(read_metadata)
    assert len(geostatsObject.sample_geotiff()) == 1000
    assert geostatsObject.mean_geotiff() < 290.
    assert geostatsObject.var_geotiff() <25.


def test_fit_leafangle_f(read_metadata):
    df = fit_leafangle_r(read_metadata)
    assert df['mean'][1] < 90.


if __name__ == '__main__':
    subprocess.call(['python -m pytest test_laser3d_stats.py -p no:cacheprovider'], shell=True)
